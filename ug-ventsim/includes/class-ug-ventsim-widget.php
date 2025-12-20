<?php
namespace UGVentSim\Widgets;

use Elementor\Widget_Base;
use Elementor\Controls_Manager;
use Elementor\Repeater;
use UGVentSim\Core\Ventilation_Engine;
use UGVentSim\Core\Equipment_Registry;
use UGVentSim\Core\UVS_Scenario_Manager;
use UGVentSim\Core\UVS_Settings;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class UGventsim_Widget extends Widget_Base {

    public function get_name() {
        return 'ug-ventsim';
    }

    public function get_title() {
        return __( 'UG-VentSim – Ventilation Simulator', 'ug-ventsim' );
    }

    public function get_icon() {
        return 'eicon-calculator';
    }

    public function get_categories() {
        return [ 'general' ];
    }

    protected function register_controls() {

        // Tab 0 – Scenario selection
        $this->start_controls_section(
            'section_scenario',
            [
                'label' => __( 'Scenario', 'ug-ventsim' ),
                'tab'   => Controls_Manager::TAB_CONTENT,
            ]
        );

        $scenarios = UVS_Scenario_Manager::list_scenarios();
        $options   = [ 0 => __( '— None / Manual Input —', 'ug-ventsim' ) ];
        foreach ( $scenarios as $sc ) {
            $options[ $sc['id'] ] = $sc['title'];
        }

        $this->add_control(
            'scenario_id',
            [
                'label'   => __( 'Load Scenario', 'ug-ventsim' ),
                'type'    => Controls_Manager::SELECT,
                'options' => $options,
                'default' => 0,
            ]
        );

        $this->add_control(
            'safety_factor',
            [
                'label'       => __( 'Safety Factor (%)', 'ug-ventsim' ),
                'type'        => Controls_Manager::SLIDER,
                'size_units'  => [ '%' ],
                'range'       => [
                    '%' => [
                        'min' => 0,
                        'max' => 30,
                        'step'=> 1,
                    ],
                ],
                'default'     => [
                    'size' => 10,
                    'unit' => '%',
                ],
                'description' => __( 'Applied on top of governing airflow.', 'ug-ventsim' ),
            ]
        );

        $this->end_controls_section();

        // Tab 1 – Heading/Stope
        $this->start_controls_section(
            'section_heading',
            [
                'label' => __( 'Heading / Stope Parameters', 'ug-ventsim' ),
                'tab'   => Controls_Manager::TAB_CONTENT,
            ]
        );

        $this->add_control(
            'width',
            [
                'label'   => __( 'Width (m)', 'ug-ventsim' ),
                'type'    => Controls_Manager::NUMBER,
                'default' => 5,
                'min'     => 0.1,
                'step'    => 0.1,
            ]
        );

        $this->add_control(
            'height',
            [
                'label'   => __( 'Height (m)', 'ug-ventsim' ),
                'type'    => Controls_Manager::NUMBER,
                'default' => 3,
                'min'     => 0.1,
                'step'    => 0.1,
            ]
        );

        $this->add_control(
            'air_density',
            [
                'label'   => __( 'Air Density (kg/m³)', 'ug-ventsim' ),
                'type'    => Controls_Manager::NUMBER,
                'default' => 1.2,
                'min'     => 0.5,
                'step'    => 0.1,
            ]
        );

        $this->add_control(
            'min_velocity',
            [
                'label'       => __( 'Minimum Air Velocity (m/s)', 'ug-ventsim' ),
                'type'        => Controls_Manager::NUMBER,
                'default'     => 0.25,
                'min'         => 0.05,
                'step'        => 0.01,
                'description' => __( 'Minimum allowable air velocity based on regulations or internal mine standards.', 'ug-ventsim' ),
            ]
        );

        $this->end_controls_section();

        // Tab 2 – Personnel & Gas
        $this->start_controls_section(
            'section_personnel_gas',
            [
                'label' => __( 'Personnel & Gas Dilution', 'ug-ventsim' ),
                'tab'   => Controls_Manager::TAB_CONTENT,
            ]
        );

        $this->add_control(
            'num_personnel',
            [
                'label'   => __( 'Number of Personnel', 'ug-ventsim' ),
                'type'    => Controls_Manager::NUMBER,
                'default' => 8,
                'min'     => 0,
                'step'    => 1,
            ]
        );

        $repeater = new Repeater();

        $repeater->add_control(
            'gas_type',
            [
                'label'   => __( 'Gas Type', 'ug-ventsim' ),
                'type'    => Controls_Manager::SELECT,
                'options' => [
                    'methane'          => __( 'Methane (CH₄)', 'ug-ventsim' ),
                    'carbon_monoxide'  => __( 'Carbon Monoxide (CO)', 'ug-ventsim' ),
                    'hydrogen_sulfide' => __( 'Hydrogen Sulfide (H₂S)', 'ug-ventsim' ),
                ],
                'default' => 'methane',
            ]
        );

        $repeater->add_control(
            'ingress_rate',
            [
                'label'   => __( 'Gas Ingress Rate (L/s)', 'ug-ventsim' ),
                'type'    => Controls_Manager::NUMBER,
                'default' => 5,
                'min'     => 0,
                'step'    => 0.1,
            ]
        );

        $this->add_control(
            'gas_sources',
            [
                'label'       => __( 'Gas Sources', 'ug-ventsim' ),
                'type'        => Controls_Manager::REPEATER,
                'fields'      => $repeater->get_controls(),
                'default'     => [],
                'title_field' => '{{{ gas_type }}} - {{{ ingress_rate }}} L/s',
            ]
        );

        $this->end_controls_section();

        // Tab 3 – Diesel Fleet
        $this->start_controls_section(
            'section_diesel',
            [
                'label' => __( 'Diesel Equipment Fleet', 'ug-ventsim' ),
                'tab'   => Controls_Manager::TAB_CONTENT,
            ]
        );

        $registry = new Equipment_Registry();
        $types    = $registry->get_equipment_types();
        $type_options = [];
        foreach ( $types as $type ) {
            $type_options[ $type ] = $type;
        }

        $equip_repeater = new Repeater();

        $equip_repeater->add_control(
            'equipment_type',
            [
                'label'   => __( 'Equipment Type', 'ug-ventsim' ),
                'type'    => Controls_Manager::SELECT,
                'options' => $type_options,
                'default' => array_key_first( $type_options ),
            ]
        );

        $equip_repeater->add_control(
            'engine_power_kw',
            [
                'label'   => __( 'Engine Power (kW)', 'ug-ventsim' ),
                'type'    => Controls_Manager::NUMBER,
                'default' => 320,
                'min'     => 0,
                'step'    => 1,
            ]
        );

        $equip_repeater->add_control(
            'ventilation_rate_factor',
            [
                'label'   => __( 'Ventilation Factor (m³/s per kW)', 'ug-ventsim' ),
                'type'    => Controls_Manager::NUMBER,
                'default' => 0.07,
                'min'     => 0,
                'step'    => 0.001,
            ]
        );

        $equip_repeater->add_control(
            'quantity',
            [
                'label'   => __( 'Active Quantity', 'ug-ventsim' ),
                'type'    => Controls_Manager::NUMBER,
                'default' => 1,
                'min'     => 0,
                'step'    => 1,
            ]
        );

        $equip_repeater->add_control(
            'utilization',
            [
                'label'      => __( 'Utilization Factor (%)', 'ug-ventsim' ),
                'type'       => Controls_Manager::SLIDER,
                'size_units' => [ '%' ],
                'range'      => [
                    '%' => [
                        'min' => 0,
                        'max' => 100,
                        'step'=> 5,
                    ],
                ],
                'default'    => [
                    'size' => 70,
                    'unit' => '%',
                ],
            ]
        );

        $this->add_control(
            'diesel_equipment',
            [
                'label'       => __( 'Diesel Fleet', 'ug-ventsim' ),
                'type'        => Controls_Manager::REPEATER,
                'fields'      => $equip_repeater->get_controls(),
                'default'     => [],
                'title_field' => '{{{ equipment_type }}} - {{{ engine_power_kw }}} kW',
            ]
        );

        $this->end_controls_section();
    }

    protected function render() {
        $settings = $this->get_settings_for_display();
        $scenario_data = [];

        if ( ! empty( $settings['scenario_id'] ) ) {
            $loaded = UVS_Scenario_Manager::load_scenario( (int) $settings['scenario_id'] );
            if ( is_array( $loaded ) ) {
                $scenario_data = $loaded;
            }
        }

        $width         = $scenario_data['width'] ?? $settings['width'];
        $height        = $scenario_data['height'] ?? $settings['height'];
        $air_density   = $scenario_data['air_density'] ?? $settings['air_density'];
        $min_velocity  = $scenario_data['min_velocity'] ?? $settings['min_velocity'];
        $num_personnel = $scenario_data['num_personnel'] ?? $settings['num_personnel'];

        $gas_sources = [];
        if ( ! empty( $scenario_data['gas_sources'] ) ) {
            foreach ( $scenario_data['gas_sources'] as $gas ) {
                $gas_sources[] = [
                    'type'         => $gas['type'],
                    'ingress_rate' => $gas['ingress_rate'],
                ];
            }
        } else {
            foreach ( $settings['gas_sources'] as $gas ) {
                $gas_sources[] = [
                    'type'         => $gas['gas_type'],
                    'ingress_rate' => $gas['ingress_rate'],
                ];
            }
        }

        $diesel_equipment = [];
        if ( ! empty( $scenario_data['diesel_equipment'] ) ) {
            $diesel_equipment = $scenario_data['diesel_equipment'];
        } else {
            foreach ( $settings['diesel_equipment'] as $eq ) {
                $diesel_equipment[] = [
                    'engine_power_kw'        => $eq['engine_power_kw'],
                    'ventilation_rate_factor'=> $eq['ventilation_rate_factor'],
                    'utilization'            => $eq['utilization']['size'] ?? 0,
                    'quantity'               => $eq['quantity'],
                ];
            }
        }

        $safety_factor = (float) ( $settings['safety_factor']['size'] ?? 0 ) / 100.0;

        $input_data = [
            'width'            => $width,
            'height'           => $height,
            'air_density'      => $air_density,
            'min_velocity'     => $min_velocity,
            'num_personnel'    => $num_personnel,
            'gas_sources'      => $gas_sources,
            'diesel_equipment' => $diesel_equipment,
            'safety_factor'    => $safety_factor,
        ];

        $engine = new Ventilation_Engine();
        $engine->set_input_data( $input_data );
        $results = $engine->get_results();

        $settings_global = UVS_Settings::get_settings();
        $unit_system     = $settings_global['unit_system'];

        $q_governing_si = $results['q_governing'];
        $q_governing_cfm = $q_governing_si * 2118.88;

        $unit_label   = $unit_system === 'imperial' ? 'cfm' : 'm³/s';
        $display_q    = $unit_system === 'imperial' ? round( $q_governing_cfm, 1 ) : $q_governing_si;
        $display_q_vel= $this->convert_unit( $results['q_velocity'], $unit_system );
        $display_q_per= $this->convert_unit( $results['q_personnel'], $unit_system );
        $display_q_gas= $this->convert_unit( $results['q_gas'], $unit_system );
        $display_q_diesel = $this->convert_unit( $results['q_diesel'], $unit_system );
        $display_q_heat   = $this->convert_unit( $results['q_heat'], $unit_system );

        ?>
        <div class="ugv-dashboard">
            <div class="ugv-main-card">
                <h3><?php esc_html_e( 'Design Airflow', 'ug-ventsim' ); ?></h3>
                <p class="ugv-main-value">
                    <?php echo esc_html( $display_q ); ?>
                    <span class="ugv-unit"><?php echo esc_html( $unit_label ); ?></span>
                </p>
                <p class="ugv-governing">
                    <?php
                    printf(
                        esc_html__( 'Governing factor: %s', 'ug-ventsim' ),
                        '<strong>' . esc_html( ucfirst( $results['governing_factor'] ) ) . '</strong>'
                    );
                    ?>
                </p>
                <p class="ugv-secondary">
                    <?php
                    printf(
                        esc_html__( 'Final air velocity: %s m/s', 'ug-ventsim' ),
                        esc_html( $results['final_velocity'] )
                    );
                    ?>
                </p>
            </div>

            <div class="ugv-grid">
                <div class="ugv-card ugv-breakdown">
                    <h4><?php esc_html_e( 'Airflow Breakdown', 'ug-ventsim' ); ?></h4>
                    <table class="ugv-table">
                        <thead>
                        <tr>
                            <th><?php esc_html_e( 'Factor', 'ug-ventsim' ); ?></th>
                            <th><?php esc_html_e( 'Required Airflow', 'ug-ventsim' ); ?></th>
                            <th><?php esc_html_e( 'Status', 'ug-ventsim' ); ?></th>
                        </tr>
                        </thead>
                        <tbody>
                        <?php
                        $rows = [
                            'velocity'  => [ __( 'Minimum Air Velocity', 'ug-ventsim' ), $display_q_vel ],
                            'personnel' => [ __( 'Personnel (Breathing)', 'ug-ventsim' ), $display_q_per ],
                            'gas'       => [ __( 'Gas Dilution', 'ug-ventsim' ), $display_q_gas ],
                            'diesel'    => [ __( 'Diesel Fleet', 'ug-ventsim' ), $display_q_diesel ],
                            'heat'      => [ __( 'Heat Load (simplified)', 'ug-ventsim' ), $display_q_heat ],
                        ];

                        foreach ( $rows as $key => $row ) :
                            $is_gov = ( $results['governing_factor'] === $key );
                            ?>
                            <tr class="<?php echo $is_gov ? 'ugv-governing-row' : ''; ?>">
                                <td><?php echo esc_html( $row[0] ); ?></td>
                                <td>
                                    <?php echo esc_html( $row[1] ); ?>
                                    <span class="ugv-unit"><?php echo esc_html( $unit_label ); ?></span>
                                </td>
                                <td><?php echo $is_gov ? esc_html__( 'Governing', 'ug-ventsim' ) : esc_html__( 'Satisfied', 'ug-ventsim' ); ?></td>
                            </tr>
                        <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>

                <div class="ugv-card ugv-chart">
                    <h4><?php esc_html_e( 'Visual Comparison', 'ug-ventsim' ); ?></h4>
                    <div class="ugv-bar-chart"
                         data-q-velocity="<?php echo esc_attr( $display_q_vel ); ?>"
                         data-q-personnel="<?php echo esc_attr( $display_q_per ); ?>"
                         data-q-gas="<?php echo esc_attr( $display_q_gas ); ?>"
                         data-q-diesel="<?php echo esc_attr( $display_q_diesel ); ?>"
                         data-q-heat="<?php echo esc_attr( $display_q_heat ); ?>"
                         data-unit="<?php echo esc_attr( $unit_label ); ?>">
                        <div class="ugv-bar ugv-bar-velocity"><span>V</span></div>
                        <div class="ugv-bar ugv-bar-personnel"><span>P</span></div>
                        <div class="ugv-bar ugv-bar-gas"><span>G</span></div>
                        <div class="ugv-bar ugv-bar-diesel"><span>D</span></div>
                        <div class="ugv-bar ugv-bar-heat"><span>H</span></div>
                    </div>
                    <p class="ugv-chart-legend">
                        <?php esc_html_e( 'Relative bar heights represent required airflow for each factor.', 'ug-ventsim' ); ?>
                    </p>
                </div>
            </div>
        </div>
        <?php
    }

    private function convert_unit( float $value_si, string $unit_system ): float {
        if ( $unit_system === 'imperial' ) {
            return round( $value_si * 2118.88, 2 );
        }
        return round( $value_si, 3 );
    }
}
