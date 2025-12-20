<?php
namespace UGVentSim\Core;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class Ventilation_Engine {

    protected float $width = 0.0;
    protected float $height = 0.0;
    protected float $area = 0.0;
    protected float $min_velocity = 0.25;
    protected float $air_density = 1.2;
    protected int $num_personnel = 0;
    protected float $air_per_person = 0.033;
    protected float $safety_factor = 0.0; // 0–0.3
    protected array $gas_sources = [];
    protected array $diesel_equipment = [];
    protected float $heat_load_kw = 0.0;

    protected array $tlv_values = [
        'methane'           => 1.0,
        'carbon_monoxide'   => 0.1,
        'hydrogen_sulfide'  => 0.05,
    ];

    protected array $results = [];

    public function set_input_data( array $data ): void {
        $this->width          = max( 0.0, floatval( $data['width'] ?? 0 ) );
        $this->height         = max( 0.0, floatval( $data['height'] ?? 0 ) );
        $this->min_velocity   = max( 0.0, floatval( $data['min_velocity'] ?? 0.25 ) );
        $this->air_density    = max( 0.1, floatval( $data['air_density'] ?? 1.2 ) );
        $this->num_personnel  = max( 0, intval( $data['num_personnel'] ?? 0 ) );
        $this->gas_sources    = $data['gas_sources'] ?? [];
        $this->diesel_equipment = $data['diesel_equipment'] ?? [];
        $this->safety_factor  = min( 0.3, max( 0.0, floatval( $data['safety_factor'] ?? 0.0 ) ) );
        $this->heat_load_kw   = max( 0.0, floatval( $data['heat_load_kw'] ?? 0.0 ) );

        $this->area = $this->width * $this->height;
    }

    protected function compute_q_velocity(): float {
        if ( $this->area <= 0 ) {
            return 0.0;
        }
        return $this->area * $this->min_velocity;
    }

    protected function compute_q_personnel(): float {
        return $this->num_personnel * $this->air_per_person;
    }

    protected function compute_q_gas(): float {
        $max_q_gas = 0.0;

        foreach ( $this->gas_sources as $gas ) {
            $ingress_l_s = floatval( $gas['ingress_rate'] ?? 0 );
            $gas_type    = strtolower( sanitize_text_field( $gas['type'] ?? 'methane' ) );
            $tlv         = $this->tlv_values[ $gas_type ] ?? 1.0;

            if ( $ingress_l_s <= 0 || $tlv <= 0 ) {
                continue;
            }

            $q_dilution = ( $ingress_l_s / 1000.0 ) * 100.0 / $tlv;
            if ( $q_dilution > $max_q_gas ) {
                $max_q_gas = $q_dilution;
            }
        }

        return $max_q_gas;
    }

    protected function compute_q_diesel(): float {
        $total_q_diesel = 0.0;

        foreach ( $this->diesel_equipment as $equipment ) {
            $power_kw   = floatval( $equipment['engine_power_kw'] ?? 0 );
            $factor     = floatval( $equipment['ventilation_rate_factor'] ?? 0 );
            $util       = floatval( $equipment['utilization'] ?? 0 ) / 100.0;
            $quantity   = intval( $equipment['quantity'] ?? 0 );

            if ( $power_kw <= 0 || $factor <= 0 || $util <= 0 || $quantity <= 0 ) {
                continue;
            }

            $total_q_diesel += $power_kw * $factor * $util * $quantity;
        }

        return $total_q_diesel;
    }

    protected function compute_q_heat(): float {
        // اسکلت ساده: Q_heat = Heat_load_kw / (specific_heat * density * ΔT)
        // برای v2 فقط به صورت placeholder:
        if ( $this->heat_load_kw <= 0 ) {
            return 0.0;
        }
        $specific_heat = 1.0; // kJ/(kg·K) – ساده
        $delta_t       = 10.0; // K – فرض
        // تبدیل kW به kJ/s: 1 kW = 1 kJ/s
        // Q = kJ/s ÷ (kJ/(m³·K) * K) → m³/s
        $kJ_per_m3K = $specific_heat * $this->air_density;
        if ( $kJ_per_m3K <= 0 || $delta_t <= 0 ) {
            return 0.0;
        }

        return $this->heat_load_kw / ( $kJ_per_m3K * $delta_t );
    }

    protected function compute_governing_q(): void {
        $q_velocity  = $this->compute_q_velocity();
        $q_personnel = $this->compute_q_personnel();
        $q_gas       = $this->compute_q_gas();
        $q_diesel    = $this->compute_q_diesel();
        $q_heat      = $this->compute_q_heat();

        $factors = [
            'velocity'  => $q_velocity,
            'personnel' => $q_personnel,
            'gas'       => $q_gas,
            'diesel'    => $q_diesel,
            'heat'      => $q_heat,
        ];

        $max_q            = max( $factors );
        $governing_factor = array_search( $max_q, $factors, true );

        $q_governing = $max_q * ( 1.0 + $this->safety_factor );

        $this->results = [
            'q_velocity'       => round( $q_velocity, 3 ),
            'q_personnel'      => round( $q_personnel, 3 ),
            'q_gas'            => round( $q_gas, 3 ),
            'q_diesel'         => round( $q_diesel, 3 ),
            'q_heat'           => round( $q_heat, 3 ),
            'q_governing_raw'  => round( $max_q, 3 ),
            'q_governing'      => round( $q_governing, 3 ),
            'governing_factor' => $governing_factor,
            'safety_factor'    => $this->safety_factor,
        ];

        $this->results['final_velocity'] = ( $this->area > 0 )
            ? round( $q_governing / $this->area, 3 )
            : 0.0;
    }

    public function get_results(): array {
        $this->compute_governing_q();
        return $this->results;
    }
}