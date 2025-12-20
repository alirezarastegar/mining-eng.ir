<?php
/**
 * Admin Interface for UG-VentSim
 */

namespace UGVentSim\Admin;

use UGVentSim\Core\Equipment_Registry;
use UGVentSim\Core\UVS_Scenario_Manager;
use UGVentSim\Core\UVS_Settings;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class UGVentSim_Admin {
    
    private Equipment_Registry $equipment_registry;
    private UVS_Scenario_Manager $scenario_manager;
    
    public function __construct() {
        $this->equipment_registry = new Equipment_Registry();
        
        add_action( 'admin_menu', [ $this, 'add_admin_menu' ] );
        add_action( 'admin_enqueue_scripts', [ $this, 'enqueue_admin_assets' ] );
        add_action( 'init', [ $this, 'register_post_types' ] );
        add_action( 'wp_ajax_uvs_add_equipment', [ $this, 'ajax_add_equipment' ] );
        add_action( 'wp_ajax_uvs_update_equipment', [ $this, 'ajax_update_equipment' ] );
        add_action( 'wp_ajax_uvs_delete_equipment', [ $this, 'ajax_delete_equipment' ] );
        add_action( 'wp_ajax_uvs_export_scenarios', [ $this, 'ajax_export_scenarios' ] );
    }
    
    public function register_post_types(): void {
        register_post_type( 'uvs_scenario', [
            'labels' => [
                'name' => __( 'Ventilation Scenarios', 'ug-ventsim' ),
                'singular_name' => __( 'Scenario', 'ug-ventsim' ),
            ],
            'public' => false,
            'show_ui' => true,
            'show_in_menu' => false,
            'supports' => [ 'title', 'editor', 'custom-fields' ],
            'capability_type' => 'post',
        ] );
    }
    
    public function add_admin_menu(): void {
        add_menu_page(
            __( 'UG-VentSim', 'ug-ventsim' ),
            __( 'UG-VentSim', 'ug-ventsim' ),
            'manage_options',
            'ug-ventsim',
            [ $this, 'render_dashboard_page' ],
            'dashicons-chart-area',
            25
        );

        add_submenu_page(
            'ug-ventsim',
            __( 'Equipment Library', 'ug-ventsim' ),
            __( 'Equipment', 'ug-ventsim' ),
            'manage_options',
            'ug-ventsim-equipment',
            [ $this, 'render_equipment_page' ]
        );

        add_submenu_page(
            'ug-ventsim',
            __( 'Scenarios', 'ug-ventsim' ),
            __( 'Scenarios', 'ug-ventsim' ),
            'manage_options',
            'ug-ventsim-scenarios',
            [ $this, 'render_scenarios_page' ]
        );

        add_submenu_page(
            'ug-ventsim',
            __( 'Settings', 'ug-ventsim' ),
            __( 'Settings', 'ug-ventsim' ),
            'manage_options',
            'ug-ventsim-settings',
            [ $this, 'render_settings_page' ]
        );
    }
    
    public function enqueue_admin_assets(): void {
        $screen = get_current_screen();
        
        if ( strpos( $screen->id ?? '', 'ug-ventsim' ) === false ) {
            return;
        }
        
        wp_enqueue_style( 'ug-ventsim-admin', UG_VENTSIM_PLUGIN_URL . 'assets/css/ug-ventsim-admin.css', [], UG_VENTSIM_VERSION );
        wp_enqueue_script( 'ug-ventsim-admin', UG_VENTSIM_PLUGIN_URL . 'assets/js/ug-ventsim-admin.js', [ 'jquery' ], UG_VENTSIM_VERSION, true );
        
        wp_localize_script( 'ug-ventsim-admin', 'ugvAdmin', [
            'ajaxUrl' => admin_url( 'admin-ajax.php' ),
            'nonce' => wp_create_nonce( 'uvs_admin_nonce' ),
            'i18n' => [
                'confirm_delete' => __( 'Are you sure?', 'ug-ventsim' ),
                'saved' => __( 'Saved successfully!', 'ug-ventsim' ),
                'error' => __( 'An error occurred', 'ug-ventsim' ),
            ],
        ] );
    }
    
    public function render_dashboard_page(): void {
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_die( esc_html__( 'Access denied', 'ug-ventsim' ) );
        }
        
        $total_equipment = count( $this->equipment_registry->get_all_equipment() );
        $total_scenarios = count( UVS_Scenario_Manager::list_scenarios() );
        
        include UG_VENTSIM_PLUGIN_DIR . 'admin/views/dashboard-page.php';
    }
    
    public function render_equipment_page(): void {
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_die( esc_html__( 'Access denied', 'ug-ventsim' ) );
        }
        
        $equipment = $this->equipment_registry->get_all_equipment();
        $types = $this->equipment_registry->get_equipment_types();
        $edit_id = isset( $_GET['edit'] ) ? intval( $_GET['edit'] ) : null;
        $edit_item = $edit_id ? $this->equipment_registry->get_equipment_spec( $edit_id ) : null;
        
        if ( isset( $_POST['ugv_equipment_nonce'] ) && wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['ugv_equipment_nonce'] ) ), 'ugv_equipment_save' ) ) {
            $this->handle_equipment_form();
        }
        
        include UG_VENTSIM_PLUGIN_DIR . 'admin/views/equipment-list.php';
    }
    
    private function handle_equipment_form(): void {
        $id = isset( $_POST['equipment_id'] ) ? intval( $_POST['equipment_id'] ) : null;
        
        $data = [
            'model_name' => sanitize_text_field( wp_unslash( $_POST['model_name'] ?? '' ) ),
            'type' => sanitize_text_field( wp_unslash( $_POST['type'] ?? '' ) ),
            'manufacturer' => sanitize_text_field( wp_unslash( $_POST['manufacturer'] ?? '' ) ),
            'engine_power_kw' => (float) ( $_POST['engine_power_kw'] ?? 0 ),
            'ventilation_rate_factor' => (float) ( $_POST['ventilation_rate_factor'] ?? 0 ),
            'exhaust_volume_cfm' => (float) ( $_POST['exhaust_volume_cfm'] ?? 0 ),
            'heat_output_kw' => (float) ( $_POST['heat_output_kw'] ?? 0 ),
            'dpm_factor' => (float) ( $_POST['dpm_factor'] ?? 0 ),
            'engine_class' => sanitize_text_field( wp_unslash( $_POST['engine_class'] ?? '' ) ),
            'notes' => wp_kses_post( wp_unslash( $_POST['notes'] ?? '' ) ),
        ];
        
        if ( $id ) {
            $this->equipment_registry->update_equipment( $id, $data );
            wp_safe_remote_post( admin_url( 'admin-ajax.php' ), [ 'blocking' => false ] );
        } else {
            $this->equipment_registry->add_equipment( $data );
        }
        
        wp_safe_redirect( admin_url( 'admin.php?page=ug-ventsim-equipment' ) );
        exit;
    }
    
    public function render_scenarios_page(): void {
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_die( esc_html__( 'Access denied', 'ug-ventsim' ) );
        }
        
        $scenarios = UVS_Scenario_Manager::list_scenarios();
        
        if ( isset( $_GET['action'], $_GET['scenario_id'], $_GET['_wpnonce'] ) ) {
            $action = sanitize_text_field( wp_unslash( $_GET['action'] ) );
            $scenario_id = intval( $_GET['scenario_id'] );
            
            if ( wp_verify_nonce( sanitize_text_field( wp_unslash( $_GET['_wpnonce'] ) ), 'uvs_scenario_action' ) ) {
                if ( 'delete' === $action ) {
                    UVS_Scenario_Manager::delete_scenario( $scenario_id );
                    wp_safe_redirect( admin_url( 'admin.php?page=ug-ventsim-scenarios' ) );
                    exit;
                }
            }
        }
        
        include UG_VENTSIM_PLUGIN_DIR . 'admin/views/scenarios-page.php';
    }
    
    public function render_settings_page(): void {
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_die( esc_html__( 'Access denied', 'ug-ventsim' ) );
        }
        
        $settings = UVS_Settings::get_settings();
        
        if ( isset( $_POST['uvs_settings_nonce'] ) && wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['uvs_settings_nonce'] ) ), 'uvs_settings_save' ) ) {
            $new_settings = [
                'unit_system' => sanitize_text_field( wp_unslash( $_POST['unit_system'] ?? 'si' ) ),
                'standard_profile' => sanitize_text_field( wp_unslash( $_POST['standard_profile'] ?? 'australian' ) ),
                'min_velocity_m' => (float) ( $_POST['min_velocity_m'] ?? 0.25 ),
                'air_density' => (float) ( $_POST['air_density'] ?? 1.2 ),
                'tlv_methane' => (float) ( $_POST['tlv_methane'] ?? 1.0 ),
                'tlv_co' => (float) ( $_POST['tlv_co'] ?? 0.1 ),
                'tlv_h2s' => (float) ( $_POST['tlv_h2s'] ?? 0.05 ),
            ];
            
            UVS_Settings::update_settings( $new_settings );
            $settings = $new_settings;
        }
        
        include UG_VENTSIM_PLUGIN_DIR . 'admin/views/settings-page.php';
    }
    
    public function ajax_add_equipment(): void {
        check_ajax_referer( 'uvs_admin_nonce', 'nonce' );
        
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_send_json_error( __( 'Permission denied', 'ug-ventsim' ) );
        }

        $data = [
            'model_name' => sanitize_text_field( wp_unslash( $_POST['model_name'] ?? '' ) ),
            'type' => sanitize_text_field( wp_unslash( $_POST['type'] ?? '' ) ),
            'manufacturer' => sanitize_text_field( wp_unslash( $_POST['manufacturer'] ?? '' ) ),
            'engine_power_kw' => (float) ( $_POST['engine_power_kw'] ?? 0 ),
            'ventilation_rate_factor' => (float) ( $_POST['ventilation_rate_factor'] ?? 0 ),
        ];
        
        $id = $this->equipment_registry->add_equipment( $data );
        
        if ( $id ) {
            wp_send_json_success( [
                'id' => $id,
                'message' => __( 'Equipment added successfully', 'ug-ventsim' ),
            ] );
        }
        
        wp_send_json_error( __( 'Failed to add equipment', 'ug-ventsim' ) );
    }
    
    public function ajax_update_equipment(): void {
        check_ajax_referer( 'uvs_admin_nonce', 'nonce' );
        
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_send_json_error( __( 'Permission denied', 'ug-ventsim' ) );
        }

        $equipment_id = intval( $_POST['equipment_id'] ?? 0 );
        
        if ( ! $equipment_id ) {
            wp_send_json_error( __( 'Invalid equipment ID', 'ug-ventsim' ) );
        }

        $data = [
            'model_name' => sanitize_text_field( wp_unslash( $_POST['model_name'] ?? '' ) ),
            'type' => sanitize_text_field( wp_unslash( $_POST['type'] ?? '' ) ),
            'manufacturer' => sanitize_text_field( wp_unslash( $_POST['manufacturer'] ?? '' ) ),
            'engine_power_kw' => (float) ( $_POST['engine_power_kw'] ?? 0 ),
            'ventilation_rate_factor' => (float) ( $_POST['ventilation_rate_factor'] ?? 0 ),
        ];
        
        if ( $this->equipment_registry->update_equipment( $equipment_id, $data ) ) {
            wp_send_json_success( [
                'message' => __( 'Equipment updated successfully', 'ug-ventsim' ),
            ] );
        }
        
        wp_send_json_error( __( 'Failed to update equipment', 'ug-ventsim' ) );
    }

    public function ajax_delete_equipment(): void {
        check_ajax_referer( 'uvs_admin_nonce', 'nonce' );
        
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_send_json_error( __( 'Permission denied', 'ug-ventsim' ) );
        }

        $equipment_id = intval( $_POST['equipment_id'] ?? 0 );
        
        if ( ! $equipment_id ) {
            wp_send_json_error( __( 'Invalid equipment ID', 'ug-ventsim' ) );
        }
        
        if ( $this->equipment_registry->delete_equipment( $equipment_id ) ) {
            wp_send_json_success( [
                'message' => __( 'Equipment deleted successfully', 'ug-ventsim' ),
            ] );
        }
        
        wp_send_json_error( __( 'Failed to delete equipment', 'ug-ventsim' ) );
    }
    
    public function ajax_export_scenarios(): void {
        check_ajax_referer( 'uvs_admin_nonce', 'nonce' );
        
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_send_json_error( __( 'Permission denied', 'ug-ventsim' ) );
        }

        UVS_Scenario_Manager::export_csv();
    }
}
?>