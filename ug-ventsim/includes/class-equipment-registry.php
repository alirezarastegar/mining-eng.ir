<?php
namespace UGVentSim\Core;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class Equipment_Registry {

    protected string $table_name;

    public function __construct() {
        global $wpdb;
        $this->table_name = $wpdb->prefix . 'uvs_diesel_equipment';
    }

    public function seed_sample_data(): void {
        global $wpdb;

        $exists = $wpdb->get_var( "SELECT COUNT(*) FROM {$this->table_name}" );
        if ( $exists > 0 ) {
            return;
        }

        $samples = [
            [ 'Epiroc ST14', 'LHD', 320, 0.07, 0 ],
            [ 'Sandvik LH517', 'LHD', 350, 0.075, 0 ],
            [ 'Volvo A45G', 'Truck', 380, 0.065, 0 ],
            [ 'CAT AD45B', 'Truck', 410, 0.07, 0 ],
            [ 'Atlas Copco Boomer XL', 'Jumbo Drill', 280, 0.06, 0 ],
            [ 'Sandvik DD422i', 'Jumbo Drill', 300, 0.062, 0 ],
        ];

        foreach ( $samples as $row ) {
            $wpdb->insert(
                $this->table_name,
                [
                    'model_name'             => $row[0],
                    'type'                   => $row[1],
                    'engine_power_kw'        => $row[2],
                    'ventilation_rate_factor'=> $row[3],
                    'exhaust_volume_cfm'     => $row[4],
                ],
                [ '%s', '%s', '%f', '%f', '%f' ]
            );
        }
    }

    public function get_equipment_types(): array {
        global $wpdb;
        $results = $wpdb->get_col( "SELECT DISTINCT type FROM {$this->table_name} ORDER BY type" );
        return $results ?: [];
    }

    public function get_models_by_type( string $type ): array {
        global $wpdb;

        $rows = $wpdb->get_results(
            $wpdb->prepare(
                "SELECT id, model_name, engine_power_kw, ventilation_rate_factor 
                 FROM {$this->table_name}
                 WHERE type = %s
                 ORDER BY model_name",
                $type
            ),
            ARRAY_A
        );

        $models = [];
        foreach ( $rows as $row ) {
            $models[] = [
                'id'     => (int) $row['id'],
                'label'  => $row['model_name'],
                'power'  => (float) $row['engine_power_kw'],
                'factor' => (float) $row['ventilation_rate_factor'],
            ];
        }

        return $models;
    }

    public function get_equipment_spec( int $id ): ?array {
        global $wpdb;

        $row = $wpdb->get_row(
            $wpdb->prepare(
                "SELECT * FROM {$this->table_name} WHERE id = %d",
                $id
            ),
            ARRAY_A
        );

        return $row ?: null;
    }

    public function create_or_update( array $data, ?int $id = null ): int {
        global $wpdb;

        $fields = [
            'model_name'             => sanitize_text_field( $data['model_name'] ?? '' ),
            'type'                   => sanitize_text_field( $data['type'] ?? '' ),
            'engine_power_kw'        => floatval( $data['engine_power_kw'] ?? 0 ),
            'ventilation_rate_factor'=> floatval( $data['ventilation_rate_factor'] ?? 0 ),
            'exhaust_volume_cfm'     => floatval( $data['exhaust_volume_cfm'] ?? 0 ),
        ];

        if ( $id ) {
            $wpdb->update(
                $this->table_name,
                $fields,
                [ 'id' => $id ],
                [ '%s', '%s', '%f', '%f', '%f' ],
                [ '%d' ]
            );
            return $id;
        }

        $wpdb->insert(
            $this->table_name,
            $fields,
            [ '%s', '%s', '%f', '%f', '%f' ]
        );

        return (int) $wpdb->insert_id;
    }

    public function delete( int $id ): void {
        global $wpdb;
        $wpdb->delete(
            $this->table_name,
            [ 'id' => $id ],
            [ '%d' ]
        );
    }

    public function get_paginated( int $paged = 1, int $per_page = 20 ): array {
        global $wpdb;

        $offset = ( $paged - 1 ) * $per_page;

        $items = $wpdb->get_results(
            $wpdb->prepare(
                "SELECT * FROM {$this->table_name} ORDER BY type, model_name LIMIT %d OFFSET %d",
                $per_page,
                $offset
            ),
            ARRAY_A
        );

        $total = (int) $wpdb->get_var( "SELECT COUNT(*) FROM {$this->table_name}" );

        return [
            'items' => $items ?: [],
            'total' => $total,
        ];
    }
}