<?php
/**
 * Plugin Name: UG-VentSim – Underground Mine Ventilation Simulator
 * Plugin URI: https://example.com/ug-ventsim
 * Description: Professional WordPress plugin for mining ventilation calculations with Elementor integration
 * Version: 2.0.0
 * Author: Your Company
 * Author URI: https://example.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: ug-ventsim
 * Domain Path: /languages
 * Requires at least: 6.0
 * Requires PHP: 8.0
 * Requires Plugins: elementor
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// Define constants
define( 'UG_VENTSIM_VERSION', '2.0.0' );
define( 'UG_VENTSIM_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );
define( 'UG_VENTSIM_PLUGIN_URL', plugin_dir_url( __FILE__ ) );
define( 'UG_VENTSIM_PLUGIN_BASENAME', plugin_basename( __FILE__ ) );

// Register activation/deactivation hooks
register_activation_hook( __FILE__, [ 'UGVentSim\Core\UGVentSim_Plugin', 'activate' ] );
register_deactivation_hook( __FILE__, [ 'UGVentSim\Core\UGVentSim_Plugin', 'deactivate' ] );

// Auto-loader for classes
spl_autoload_register( function( $class ) {
    if ( strpos( $class, 'UGVentSim' ) !== 0 ) {
        return;
    }
    
    $path = str_replace( '\\', DIRECTORY_SEPARATOR, $class );
    $path = str_replace( 'UGVentSim' . DIRECTORY_SEPARATOR, '', $path );
    
    $file = UG_VENTSIM_PLUGIN_DIR . 'includes' . DIRECTORY_SEPARATOR;
    
    if ( strpos( $path, 'Admin' ) === 0 ) {
        $file = UG_VENTSIM_PLUGIN_DIR . 'admin' . DIRECTORY_SEPARATOR;
    }
    
    if ( strpos( $path, 'Widgets' ) === 0 ) {
        $file = UG_VENTSIM_PLUGIN_DIR . 'includes' . DIRECTORY_SEPARATOR;
    }
    
    $file .= 'class-' . strtolower( str_replace( '\\', '-', $path ) ) . '.php';
    
    if ( file_exists( $file ) ) {
        require_once $file;
    }
} );

// Initialize plugin on plugins_loaded hook
add_action( 'plugins_loaded', function() {
    // Load text domain
    load_plugin_textdomain( 'ug-ventsim', false, dirname( plugin_basename( __FILE__ ) ) . '/languages' );
    
    // Check if Elementor is active
    if ( ! did_action( 'elementor/loaded' ) ) {
        add_action( 'admin_notices', function() {
            ?>
            <div class="notice notice-error is-dismissible">
                <p>
                    <strong><?php esc_html_e( 'UG-VentSim', 'ug-ventsim' ); ?></strong>
                    <?php esc_html_e( 'requires Elementor Pro to be installed and activated.', 'ug-ventsim' ); ?>
                </p>
            </div>
            <?php
        } );
        return;
    }
    
    // Register Elementor widget
    add_action( 'elementor/widgets/register', function( $widgets_manager ) {
        if ( class_exists( 'UGVentSim\Widgets\UGVentSim_Widget' ) ) {
            $widgets_manager->register( new \UGVentSim\Widgets\UGVentSim_Widget() );
        }
    } );
    
    // Initialize admin interface
    if ( is_admin() ) {
        if ( class_exists( 'UGVentSim\Admin\UGVentSim_Admin' ) ) {
            new \UGVentSim\Admin\UGVentSim_Admin();
        }
    }
    
    // Initialize AJAX handlers
    if ( class_exists( 'UGVentSim\Core\UVS_Ajax' ) ) {
        new \UGVentSim\Core\UVS_Ajax();
    }
    
    // Initialize settings
    if ( class_exists( 'UGVentSim\Core\UVS_Settings' ) ) {
        new \UGVentSim\Core\UVS_Settings();
    }
} );

// Enqueue frontend assets
add_action( 'wp_enqueue_scripts', function() {
    wp_enqueue_style( 'ug-ventsim-styles', UG_VENTSIM_PLUGIN_URL . 'assets/css/ug-ventsim-styles.css', [], UG_VENTSIM_VERSION );
    wp_enqueue_script( 'ug-ventsim-scripts', UG_VENTSIM_PLUGIN_URL . 'assets/js/ug-ventsim-scripts.js', [ 'jquery' ], UG_VENTSIM_VERSION, true );
    
    wp_localize_script( 'ug-ventsim-scripts', 'ugvFrontend', [
        'ajaxUrl' => admin_url( 'admin-ajax.php' ),
        'nonce' => wp_create_nonce( 'uvs_nonce' ),
    ] );
} );
