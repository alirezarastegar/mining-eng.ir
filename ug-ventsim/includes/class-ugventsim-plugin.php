<?php
namespace UGVentSim\Core;

use UGVentSim\Core\Equipment_Registry;
use UGVentSim\Core\UVS_Scenario_Manager;
use UGVentSim\Core\UVS_Settings;
use UGVentSim\Widgets\UGVentSim_Widget;
use UGVentSim\Admin\UGVentSim_Admin;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class UGventsim_Plugin {

    private static ?UGventsim_Plugin $instance = null;

    public static function instance(): UGventsim_Plugin {
        if ( self::$instance === null ) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    public static function activate(): void {
        // ساخت جدول تجهیزات دیزل
        self::create_diesel_table();
        // seed داده نمونه
        $registry = new Equipment_Registry();
        $registry->seed_sample_data();
        // ثبت CPT سناریو و ایجاد سناریوهای نمونه
        UVS_Scenario_Manager::register_cpt();
        UVS_Scenario_Manager::seed_sample_scenarios();
    }

    public static function deactivate(): void {
        // فعلاً دیتابیس را پاک نمی‌کنیم
    }

    private function __construct() {
        // CPT سناریو
        add_action( 'init', [ UVS_Scenario_Manager::class, 'register_cpt' ] );
        // تنظیمات سراسری
        add_action( 'admin_init', [ UVS_Settings::class, 'register_settings' ] );
        // Elementor – ویجت
        add_action( 'elementor/widgets/register', [ $this, 'register_elementor_widget' ] );
        // Scripts / Styles
        add_action( 'wp_enqueue_scripts', [ $this, 'register_front_assets' ] );
        add_action( 'elementor/frontend/widget/before_render', [ $this, 'conditionally_enqueue_front_assets' ], 10, 1 );
        add_action( 'elementor/preview/enqueue_scripts', [ $this, 'enqueue_front_assets_preview' ] );
        // Ajax
        UVS_Ajax::register();
        // Admin
        if ( is_admin() ) {
            new UGventsim_Admin();
        }
    }

    private static function create_diesel_table(): void {
        global $wpdb;
        $table_name      = $wpdb->prefix . 'uvs_diesel_equipment';
        $charset_collate = $wpdb->get_charset_collate();

        $sql = "CREATE TABLE {$table_name} (
            id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
            model_name varchar(191) NOT NULL,
            type varchar(50) NOT NULL,
            engine_power_kw float NOT NULL,
            ventilation_rate_factor float NOT NULL,
            exhaust_volume_cfm float DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY  (id),
            KEY type (type),
            UNIQUE KEY model_name (model_name)
        ) {$charset_collate};";

        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
        dbDelta( $sql );
    }

    public function register_elementor_widget( $widgets_manager ): void {
        $widgets_manager->register( new UGventsim_Widget() );
    }

    public function register_front_assets(): void {
        wp_register_style(
            'ug-ventsim-frontend',
            UG_VENTSIM_PLUGIN_URL . 'assets/css/ug-ventsim-styles.css',
            [],
            UG_VENTSIM_VERSION
        );

        wp_register_script(
            'ug-ventsim-frontend',
            UG_VENTSIM_PLUGIN_URL . 'assets/js/ug-ventsim-scripts.js',
            [ 'jquery' ],
            UG_VENTSIM_VERSION,
            true
        );

        wp_localize_script(
            'ug-ventsim-frontend',
            'UGVentSimAjax',
            [
                'ajax_url' => admin_url( 'admin-ajax.php' ),
                'nonce'    => wp_create_nonce( 'ugv_ajax_nonce' ),
            ]
        );
    }

    public function conditionally_enqueue_front_assets( $widget ): void {
        if ( $widget->get_name() === 'ug-ventsim' ) {
            wp_enqueue_style( 'ug-ventsim-frontend' );
            wp_enqueue_script( 'ug-ventsim-frontend' );
        }
    }

    public function enqueue_front_assets_preview(): void {
        wp_enqueue_style( 'ug-ventsim-frontend' );
        wp_enqueue_script( 'ug-ventsim-frontend' );
    }
}
