<?php
namespace UGVentSim\Core;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class UVS_Ajax {

    public static function register(): void {
        add_action( 'wp_ajax_ugv_save_scenario', [ self::class, 'save_scenario' ] );
        add_action( 'wp_ajax_ugv_load_scenario', [ self::class, 'load_scenario' ] );
        add_action( 'wp_ajax_ugv_get_scenarios', [ self::class, 'get_scenarios' ] );
    }

    protected static function check_nonce(): void {
        if ( ! isset( $_POST['nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['nonce'] ) ), 'ugv_ajax_nonce' ) ) {
            wp_send_json_error( [ 'message' => 'Invalid nonce' ], 403 );
        }
    }

    public static function save_scenario(): void {
        self::check_nonce();
        if ( ! current_user_can( 'edit_posts' ) ) {
            wp_send_json_error( [ 'message' => 'No permission' ], 403 );
        }

        $title = sanitize_text_field( wp_unslash( $_POST['title'] ?? 'Saved Scenario' ) );
        $data  = json_decode( stripslashes( $_POST['data'] ?? '[]' ), true );
        if ( ! is_array( $data ) ) {
            wp_send_json_error( [ 'message' => 'Invalid data' ], 400 );
        }

        $id = UVS_Scenario_Manager::save_scenario( $title, $data );
        wp_send_json_success( [ 'id' => $id ] );
    }

    public static function load_scenario(): void {
        self::check_nonce();

        $id = intval( $_POST['id'] ?? 0 );
        if ( ! $id ) {
            wp_send_json_error( [ 'message' => 'Invalid ID' ], 400 );
        }

        $data = UVS_Scenario_Manager::load_scenario( $id );
        if ( ! $data ) {
            wp_send_json_error( [ 'message' => 'Not found' ], 404 );
        }

        wp_send_json_success( [ 'data' => $data ] );
    }

    public static function get_scenarios(): void {
        self::check_nonce();

        $list = UVS_Scenario_Manager::list_scenarios();
        wp_send_json_success( [ 'scenarios' => $list ] );
    }
}