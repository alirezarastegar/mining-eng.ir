<?php
namespace UGVentSim\Core;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class UVS_Scenario_Manager {

    /**
     * Register CPT and hooks
     */
    public static function init() {
        add_action( 'init', [ __CLASS__, 'register_cpt' ] );
    }

    /**
     * Register custom post type for scenarios
     */
    public static function register_cpt() {
        $labels = [
            'name'               => __( 'Ventilation Scenarios', 'ug-ventsim' ),
            'singular_name'      => __( 'Ventilation Scenario', 'ug-ventsim' ),
            'add_new'            => __( 'Add New', 'ug-ventsim' ),
            'add_new_item'       => __( 'Add New Scenario', 'ug-ventsim' ),
            'edit_item'          => __( 'Edit Scenario', 'ug-ventsim' ),
            'new_item'           => __( 'New Scenario', 'ug-ventsim' ),
            'all_items'          => __( 'All Scenarios', 'ug-ventsim' ),
            'view_item'          => __( 'View Scenario', 'ug-ventsim' ),
            'search_items'       => __( 'Search Scenarios', 'ug-ventsim' ),
            'not_found'          => __( 'No scenarios found', 'ug-ventsim' ),
            'not_found_in_trash' => __( 'No scenarios found in Trash', 'ug-ventsim' ),
            'menu_name'          => __( 'Ventilation Scenarios', 'ug-ventsim' ),
        ];

        $args = [
            'labels'             => $labels,
            'public'             => false,
            'show_ui'            => false, // مدیریت از طریق صفحه اختصاصی پلاگین
            'show_in_menu'       => false,
            'capability_type'    => 'post',
            'supports'           => [ 'title', 'editor' ],
            'hierarchical'       => false,
        ];

        register_post_type( 'uvs_scenario', $args );
    }

    /**
     * Create or update a scenario
     *
     * @param array $data
     * @param int|null $post_id
     * @return int|WP_Error
     */
    public static function save_scenario( array $data, ?int $post_id = null ) {
        $title       = sanitize_text_field( $data['title'] ?? '' );
        $description = sanitize_textarea_field( $data['description'] ?? '' );
        $payload     = $data['payload'] ?? [];

        if ( empty( $title ) ) {
            return new \WP_Error( 'uvs_no_title', __( 'Scenario title is required.', 'ug-ventsim' ) );
        }

        $postarr = [
            'post_type'    => 'uvs_scenario',
            'post_status'  => 'publish',
            'post_title'   => $title,
            'post_content' => $description,
        ];

        if ( $post_id ) {
            $postarr['ID'] = $post_id;
            $post_id = wp_update_post( $postarr, true );
        } else {
            $post_id = wp_insert_post( $postarr, true );
        }

        if ( is_wp_error( $post_id ) ) {
            return $post_id;
        }

        // ذخیره داده‌های سناریو
        update_post_meta( $post_id, 'uvs_scenario_data', wp_json_encode( $payload ) );

        return $post_id;
    }

    /**
     * Load scenario by ID
     *
     * @param int $post_id
     * @return array|null
     */
    public static function load_scenario( int $post_id ): ?array {
        $post = get_post( $post_id );

        if ( ! $post || 'uvs_scenario' !== $post->post_type ) {
            return null;
        }

        $raw = get_post_meta( $post_id, 'uvs_scenario_data', true );
        $data = is_string( $raw ) ? json_decode( $raw, true ) : (array) $raw;

        if ( ! is_array( $data ) ) {
            $data = [];
        }

        $data['id']          = $post_id;
        $data['title']       = $post->post_title;
        $data['description'] = $post->post_content;

        return $data;
    }

    /**
     * Duplicate scenario
     *
     * @param int $post_id
     * @return int|WP_Error
     */
    public static function duplicate_scenario( int $post_id ) {
        $scenario = self::load_scenario( $post_id );

        if ( ! $scenario ) {
            return new \WP_Error( 'uvs_not_found', __( 'Scenario not found.', 'ug-ventsim' ) );
        }

        unset( $scenario['id'] );

        $scenario['title'] = $scenario['title'] . ' (Copy)';

        return self::save_scenario( [
            'title'       => $scenario['title'],
            'description' => $scenario['description'] ?? '',
            'payload'     => $scenario,
        ] );
    }

    /**
     * Delete scenario
     *
     * @param int $post_id
     * @return bool
     */
    public static function delete_scenario( int $post_id ): bool {
        $post = get_post( $post_id );

        if ( ! $post || 'uvs_scenario' !== $post->post_type ) {
            return false;
        }

        wp_delete_post( $post_id, true );

        return true;
    }

    /**
     * List scenarios for dropdowns / admin
     *
     * @return array[]
     */
    public static function list_scenarios(): array {
        $posts = get_posts( [
            'post_type'      => 'uvs_scenario',
            'posts_per_page' => -1,
            'orderby'        => 'date',
            'order'          => 'DESC',
        ] );

        $items = [];

        foreach ( $posts as $post ) {
            $items[] = [
                'id'    => $post->ID,
                'title' => $post->post_title,
            ];
        }

        return $items;
    }

    /**
     * Export scenarios as CSV string
     *
     * @return string
     */
    public static function export_csv(): string {
        $scenarios = get_posts( [
            'post_type'      => 'uvs_scenario',
            'posts_per_page' => -1,
            'orderby'        => 'date',
            'order'          => 'DESC',
        ] );

        $rows   = [];
        $header = [
            'id',
            'title',
            'description',
            'data_json',
        ];

        $rows[] = $header;

        foreach ( $scenarios as $post ) {
            $raw  = get_post_meta( $post->ID, 'uvs_scenario_data', true );
            $rows[] = [
                $post->ID,
                $post->post_title,
                $post->post_content,
                $raw,
            ];
        }

        // تبدیل به CSV
        $fh = fopen( 'php://temp', 'r+' );

        foreach ( $rows as $row ) {
            fputcsv( $fh, $row );
        }

        rewind( $fh );
        $csv = stream_get_contents( $fh );
        fclose( $fh );

        return (string) $csv;
    }

    /**
     * Import scenarios from CSV content
     *
     * @param string $csv
     * @return int تعداد سناریوهای ایمپورت شده
     */
    public static function import_csv( string $csv ): int {
        $fh = fopen( 'php://temp', 'r+' );
        fwrite( $fh, $csv );
        rewind( $fh );

        $count  = 0;
        $header = null;

        while ( ( $row = fgetcsv( $fh ) ) !== false ) {
            if ( ! $header ) {
                $header = $row;
                continue;
            }

            $data = array_combine( $header, $row );

            if ( ! $data ) {
                continue;
            }

            $title       = $data['title'] ?? '';
            $description = $data['description'] ?? '';
            $json        = $data['data_json'] ?? '';

            $payload = [];
            if ( ! empty( $json ) ) {
                $decoded = json_decode( $json, true );
                if ( is_array( $decoded ) ) {
                    $payload = $decoded;
                }
            }

            $result = self::save_scenario( [
                'title'       => $title,
                'description' => $description,
                'payload'     => $payload,
            ] );

            if ( ! is_wp_error( $result ) ) {
                $count++;
            }
        }

        fclose( $fh );

        return $count;
    }
}