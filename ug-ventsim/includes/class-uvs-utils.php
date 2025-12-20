<?php
namespace UGVentSim\Core;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class UVS_Ajax {

    const NONCE_ACTION = 'uvs_ajax_nonce';

    /**
     * Register AJAX hooks
     */
    public static function init() {
        // سناریوها
        add_action( 'wp_ajax_uvs_save_scenario', [ __CLASS__, 'save_scenario' ] );
        add_action( 'wp_ajax_uvs_load_scenario', [ __CLASS__, 'load_scenario' ] );
        add_action( 'wp_ajax_uvs_duplicate_scenario', [ __CLASS__, 'duplicate_scenario' ] );
        add_action( 'wp_ajax_uvs_delete_scenario', [ __CLASS__, 'delete_scenario' ] );

        // Export / Import
        add_action( 'admin_post_uvs_export_scenarios', [ __CLASS__, 'export_scenarios' ] );
        add_action( 'admin_post_uvs_import_scenarios', [ __CLASS__, 'import_scenarios' ] );

        // Localize nonce & ajaxurl در اسکریپت‌ها (در کلاس Admin/Frontend انجام می‌شود)
    }

    /**
     * Save scenario from frontend or admin
     */
    public static function save_scenario() {
        UVS_Utils::verify_ajax_nonce( self::NONCE_ACTION );

        if ( ! current_user_can( 'edit_posts' ) ) {
            wp_send_json_error( [ 'message' => __( 'Permission denied.', 'ug-ventsim' ) ], 403 );
        }

        $title       = sanitize_text_field( $_POST['title'] ?? '' );
        $description = sanitize_textarea_field( $_POST['description'] ?? '' );
        $payload     = isset( $_POST['payload'] ) ? wp_unslash( $_POST['payload'] ) : '';

        if ( empty( $title ) ) {
            wp_send_json_error( [ 'message' => __( 'Title is required.', 'ug-ventsim' ) ], 400 );
        }

        $decoded = [];
        if ( ! empty( $payload ) ) {
            $tmp = json_decode( $payload, true );
            if ( is_array( $tmp ) ) {
                $decoded = $tmp;
            }
        }

        $post_id = isset( $_POST['id'] ) ? (int) $_POST['id'] : null;

        $result = UVS_Scenario_Manager::save_scenario( [
            'title'       => $title,
            'description' => $description,
            'payload'     => $decoded,
        ], $post_id );

        if ( is_wp_error( $result ) ) {
            wp_send_json_error( [ 'message' => $result->get_error_message() ], 400 );
        }

        wp_send_json_success( [
            'id'      => $result,
            'message' => __( 'Scenario saved successfully.', 'ug-ventsim' ),
        ] );
    }

    /**
     * Load scenario
     */
    public static function load_scenario() {
        UVS_Utils::verify_ajax_nonce( self::NONCE_ACTION );

        $id = isset( $_POST['id'] ) ? (int) $_POST['id'] : 0;

        if ( ! $id ) {
            wp_send_json_error( [ 'message' => __( 'Invalid scenario ID.', 'ug-ventsim' ) ], 400 );
        }

        $scenario = UVS_Scenario_Manager::load_scenario( $id );

        if ( ! $scenario ) {
            wp_send_json_error( [ 'message' => __( 'Scenario not found.', 'ug-ventsim' ) ], 404 );
        }

        wp_send_json_success( [
            'scenario' => $scenario,
        ] );
    }

    /**
     * Duplicate scenario
     */
    public static function duplicate_scenario() {
        UVS_Utils::verify_ajax_nonce( self::NONCE_ACTION );

        if ( ! current_user_can( 'edit_posts' ) ) {
            wp_send_json_error( [ 'message' => __( 'Permission denied.', 'ug-ventsim' ) ], 403 );
        }

        $id = isset( $_POST['id'] ) ? (int) $_POST['id'] : 0;

        if ( ! $id ) {
            wp_send_json_error( [ 'message' => __( 'Invalid scenario ID.', 'ug-ventsim' ) ], 400 );
        }

        $result = UVS_Scenario_Manager::duplicate_scenario( $id );

        if ( is_wp_error( $result ) ) {
            wp_send_json_error( [ 'message' => $result->get_error_message() ], 400 );
        }

        wp_send_json_success( [
            'id'      => $result,
            'message' => __( 'Scenario duplicated.', 'ug-ventsim' ),
        ] );
    }

    /**
     * Delete scenario
     */
    public static function delete_scenario() {
        UVS_Utils::verify_ajax_nonce( self::NONCE_ACTION );

        if ( ! current_user_can( 'delete_posts' ) ) {
            wp_send_json_error( [ 'message' => __( 'Permission denied.', 'ug-ventsim' ) ], 403 );
        }

        $id = isset( $_POST['id'] ) ? (int) $_POST['id'] : 0;

        if ( ! $id ) {
            wp_send_json_error( [ 'message' => __( 'Invalid scenario ID.', 'ug-ventsim' ) ], 400 );
        }

        $ok = UVS_Scenario_Manager::delete_scenario( $id );

        if ( ! $ok ) {
            wp_send_json_error( [ 'message' => __( 'Scenario not found.', 'ug-ventsim' ) ], 404 );
        }

        wp_send_json_success( [
            'message' => __( 'Scenario deleted.', 'ug-ventsim' ),
        ] );
    }

    /**
     * Export scenarios as CSV (admin_post)
     */
    public static function export_scenarios() {
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_die( __( 'Permission denied.', 'ug-ventsim' ) );
        }

        check_admin_referer( 'uvs_export_scenarios' );

        $csv = UVS_Scenario_Manager::export_csv();

        UVS_Utils::send_csv_download( 'ug-ventsim-scenarios.csv', $csv );
    }

    /**
     * Import scenarios from uploaded CSV (admin_post)
     */
    public static function import_scenarios() {
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_die( __( 'Permission denied.', 'ug-ventsim' ) );
        }

        check_admin_referer( 'uvs_import_scenarios' );

        if ( empty( $_FILES['uvs_import_file']['tmp_name'] ) ) {
            wp_redirect( add_query_arg( [ 'page' => 'ug-ventsim-scenarios', 'uvs_import' => '0' ], admin_url( 'admin.php' ) ) );
            exit;
        }

        $csv = file_get_contents( $_FILES['uvs_import_file']['tmp_name'] );

        if ( false === $csv ) {
            wp_redirect( add_query_arg( [ 'page' => 'ug-ventsim-scenarios', 'uvs_import' => '0' ], admin_url( 'admin.php' ) ) );
            exit;
        }

        $count = UVS_Scenario_Manager::import_csv( $csv );

        wp_redirect( add_query_arg( [ 'page' => 'ug-ventsim-scenarios', 'uvs_import' => $count ], admin_url( 'admin.php' ) ) );
        exit;
    }
}
