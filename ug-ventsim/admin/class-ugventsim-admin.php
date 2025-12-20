<?php
namespace UGVentSim\Admin;

use UGVentSim\Core\Equipment_Registry;
use UGVentSim\Core\UVS_Settings;
use UGVentSim\Core\UVS_Scenario_Manager;
use UGVentSim\Core\UVS_Ajax;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class UGventsim_Admin {

    public function __construct() {
        add_action( 'admin_menu', [ $this, 'register_menu' ] );
        add_action( 'admin_enqueue_scripts', [ $this, 'enqueue_assets' ] );

        // سناریو و AJAX را هم اینجا initial می‌کنیم
        UVS_Scenario_Manager::init();
        UVS_Ajax::init();
    }

    public function register_menu(): void {
        // منوی اصلی
        add_menu_page(
            __( 'UG VentSim', 'ug-ventsim' ),
            __( 'UG VentSim', 'ug-ventsim' ),
            'manage_options',
            'ug-ventsim',
            [ $this, 'render_equipment_page' ],
            'dashicons-chart-area'
        );

        // Submenu: Diesel Equipment (همان صفحه اصلی)
        add_submenu_page(
            'ug-ventsim',
            __( 'Diesel Equipment', 'ug-ventsim' ),
            __( 'Diesel Equipment', 'ug-ventsim' ),
            'manage_options',
            'ug-ventsim',
            [ $this, 'render_equipment_page' ]
        );

        // Submenu: Scenarios
        add_submenu_page(
            'ug-ventsim',
            __( 'Ventilation Scenarios', 'ug-ventsim' ),
            __( 'Scenarios', 'ug-ventsim' ),
            'edit_posts',
            'ug-ventsim-scenarios',
            [ $this, 'render_scenarios_page' ]
        );

        // Submenu: Settings
        add_submenu_page(
            'ug-ventsim',
            __( 'Settings', 'ug-ventsim' ),
            __( 'Settings', 'ug-ventsim' ),
            'manage_options',
            'ug-ventsim-settings',
            [ $this, 'render_settings_page' ]
        );
    }

    public function enqueue_assets( $hook ): void {
        if ( strpos( $hook, 'ug-ventsim' ) === false ) {
            return;
        }

        wp_enqueue_style(
            'ug-ventsim-admin',
            UG_VENTSIM_PLUGIN_URL . 'assets/css/ug-ventsim-admin.css',
            [],
            UG_VENTSIM_VERSION
        );

        wp_enqueue_script(
            'ug-ventsim-admin',
            UG_VENTSIM_PLUGIN_URL . 'assets/js/ug-ventsim-admin.js',
            [ 'jquery' ],
            UG_VENTSIM_VERSION,
            true
        );

        // برای AJAX سناریوها
        wp_localize_script(
            'ug-ventsim-admin',
            'UGVentSimAdmin',
            [
                'ajax_url' => admin_url( 'admin-ajax.php' ),
                'nonce'    => wp_create_nonce( UVS_Ajax::NONCE_ACTION ),
                'i18n'     => [
                    'confirm_delete' => __( 'Delete this scenario?', 'ug-ventsim' ),
                ],
            ]
        );
    }

    /**
     * صفحه Equipment (همان کدی که خودت دادی + بدون تغییر در ساختار)
     */
    public function render_equipment_page(): void {
        if ( ! current_user_can( 'manage_options' ) ) {
            return;
        }

        $registry = new Equipment_Registry();

        if (
            isset( $_POST['ugv_equipment_nonce'] ) &&
            wp_verify_nonce(
                sanitize_text_field( wp_unslash( $_POST['ugv_equipment_nonce'] ) ),
                'ugv_equipment_save'
            ) &&
            isset( $_POST['model_name'] )
        ) {
            $id = isset( $_POST['id'] ) ? intval( $_POST['id'] ) : null;

            // در کلاس Equipment_Registry فعلی‌ات متد create_or_update نیست،
            // اگر خواستی می‌توانیم آن را اضافه کنیم؛ فعلاً فرض می‌کنیم همان متد add/update که داری را صدا می‌زنی.
            $data = [
                'model_name'              => wp_unslash( $_POST['model_name'] ?? '' ),
                'type'                    => wp_unslash( $_POST['type'] ?? '' ),
                'manufacturer'            => wp_unslash( $_POST['manufacturer'] ?? '' ),
                'engine_power_kw'         => (float) ( $_POST['engine_power_kw'] ?? 0 ),
                'ventilation_rate_factor' => (float) ( $_POST['ventilation_rate_factor'] ?? 0 ),
                'exhaust_volume_cfm'      => (float) ( $_POST['exhaust_volume_cfm'] ?? 0 ),
            ];

            if ( $id ) {
                $registry->update_equipment( $id, $data );
            } else {
                $registry->add_equipment( $data );
            }

            echo '<div class="notice notice-success"><p>' . esc_html__( 'Equipment saved.', 'ug-ventsim' ) . '</p></div>';
        }

        if ( isset( $_GET['action'], $_GET['id'] ) && $_GET['action'] === 'delete' ) {
            $del_id = intval( $_GET['id'] );
            check_admin_referer( 'ugv_equipment_delete_' . $del_id );
            $registry->delete_equipment( $del_id );
            echo '<div class="notice notice-success"><p>' . esc_html__( 'Equipment deleted.', 'ug-ventsim' ) . '</p></div>';
        }

        // این بخش در نسخه‌ای که فرستادی از متد get_paginated استفاده می‌کرد؛ در کلاس فعلی‌equipment چنین متدی نداری.
        // فعلاً ساده همه را می‌گیریم؛ اگر خواستی بعداً pagination را اضافه می‌کنیم.
        $items = $registry->get_all_equipment();

        ?>
        <div class="wrap">
            <h1><?php esc_html_e( 'Diesel Ventilation Equipment', 'ug-ventsim' ); ?></h1>

            <form method="post" style="margin-top:20px;">
                <?php wp_nonce_field( 'ugv_equipment_save', 'ugv_equipment_nonce' ); ?>
                <table class="form-table">
                    <tr>
                        <th><label for="model_name"><?php esc_html_e( 'Model Name', 'ug-ventsim' ); ?></label></th>
                        <td><input type="text" name="model_name" id="model_name" class="regular-text" required></td>
                    </tr>
                    <tr>
                        <th><label for="type"><?php esc_html_e( 'Type', 'ug-ventsim' ); ?></label></th>
                        <td><input type="text" name="type" id="type" class="regular-text" required></td>
                    </tr>
                    <tr>
                        <th><label for="manufacturer"><?php esc_html_e( 'Manufacturer', 'ug-ventsim' ); ?></label></th>
                        <td><input type="text" name="manufacturer" id="manufacturer" class="regular-text"></td>
                    </tr>
                    <tr>
                        <th><label for="engine_power_kw"><?php esc_html_e( 'Engine Power (kW)', 'ug-ventsim' ); ?></label></th>
                        <td><input type="number" step="0.1" name="engine_power_kw" id="engine_power_kw" required></td>
                    </tr>
                    <tr>
                        <th><label for="ventilation_rate_factor"><?php esc_html_e( 'Ventilation Factor (m³/s per kW)', 'ug-ventsim' ); ?></label></th>
                        <td><input type="number" step="0.001" name="ventilation_rate_factor" id="ventilation_rate_factor" required></td>
                    </tr>
                    <tr>
                        <th><label for="exhaust_volume_cfm"><?php esc_html_e( 'Exhaust Volume (cfm)', 'ug-ventsim' ); ?></label></th>
                        <td><input type="number" step="0.1" name="exhaust_volume_cfm" id="exhaust_volume_cfm"></td>
                    </tr>
                </table>
                <?php submit_button( __( 'Add / Update Equipment', 'ug-ventsim' ) ); ?>
            </form>

            <h2 style="margin-top:40px;"><?php esc_html_e( 'Equipment List', 'ug-ventsim' ); ?></h2>
            <table class="widefat striped">
                <thead>
                    <tr>
                        <th><?php esc_html_e( 'Model', 'ug-ventsim' ); ?></th>
                        <th><?php esc_html_e( 'Type', 'ug-ventsim' ); ?></th>
                        <th><?php esc_html_e( 'Manufacturer', 'ug-ventsim' ); ?></th>
                        <th><?php esc_html_e( 'Power (kW)', 'ug-ventsim' ); ?></th>
                        <th><?php esc_html_e( 'Ventilation Factor', 'ug-ventsim' ); ?></th>
                        <th><?php esc_html_e( 'Actions', 'ug-ventsim' ); ?></th>
                    </tr>
                </thead>
                <tbody>
                <?php if ( ! empty( $items ) ) : ?>
                    <?php foreach ( $items as $item ) : ?>
                        <tr>
                            <td><?php echo esc_html( $item['model_name'] ); ?></td>
                            <td><?php echo esc_html( $item['type'] ); ?></td>
                            <td><?php echo esc_html( $item['manufacturer'] ); ?></td>
                            <td><?php echo esc_html( $item['engine_power_kw'] ); ?></td>
                            <td><?php echo esc_html( $item['ventilation_rate_factor'] ); ?></td>
                            <td>
                                <a href="<?php echo esc_url(
                                    wp_nonce_url(
                                        add_query_arg(
                                            [
                                                'page'   => 'ug-ventsim',
                                                'action' => 'delete',
                                                'id'     => $item['id'],
                                            ],
                                            admin_url( 'admin.php' )
                                        ),
                                        'ugv_equipment_delete_' . $item['id']
                                    )
                                ); ?>"
                                   onclick="return confirm('<?php echo esc_attr__( 'Delete this item?', 'ug-ventsim' ); ?>');">
                                    <?php esc_html_e( 'Delete', 'ug-ventsim' ); ?>
                                </a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                <?php else : ?>
                    <tr><td colspan="6"><?php esc_html_e( 'No equipment found.', 'ug-ventsim' ); ?></td></tr>
                <?php endif; ?>
                </tbody>
            </table>
        </div>
        <?php
    }

    /**
     * صفحه مدیریت سناریوها
     */
    public function render_scenarios_page(): void {
        if ( ! current_user_can( 'edit_posts' ) ) {
            return;
        }

        $scenarios = UVS_Scenario_Manager::list_scenarios();
        ?>
        <div class="wrap">
            <h1><?php esc_html_e( 'Ventilation Scenarios', 'ug-ventsim' ); ?></h1>

            <p><?php esc_html_e( 'Use the Elementor widget to create and save scenarios. They will appear here.', 'ug-ventsim' ); ?></p>

            <form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" style="margin-bottom:20px;">
                <?php wp_nonce_field( 'uvs_export_scenarios' ); ?>
                <input type="hidden" name="action" value="uvs_export_scenarios">
                <?php submit_button( __( 'Export All Scenarios (CSV)', 'ug-ventsim' ), 'secondary', 'submit', false ); ?>
            </form>

            <form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" enctype="multipart/form-data" style="margin-bottom:20px;">
                <?php wp_nonce_field( 'uvs_import_scenarios' ); ?>
                <input type="hidden" name="action" value="uvs_import_scenarios">
                <input type="file" name="uvs_import_file" accept=".csv" required>
                <?php submit_button( __( 'Import Scenarios from CSV', 'ug-ventsim' ), 'secondary', 'submit', false ); ?>
            </form>

            <table class="widefat striped">
                <thead>
                    <tr>
                        <th><?php esc_html_e( 'ID', 'ug-ventsim' ); ?></th>
                        <th><?php esc_html_e( 'Title', 'ug-ventsim' ); ?></th>
                    </tr>
                </thead>
                <tbody>
                <?php if ( ! empty( $scenarios ) ) : ?>
                    <?php foreach ( $scenarios as $sc ) : ?>
                        <tr>
                            <td><?php echo esc_html( $sc['id'] ); ?></td>
                            <td><?php echo esc_html( $sc['title'] ); ?></td>
                        </tr>
                    <?php endforeach; ?>
                <?php else : ?>
                    <tr><td colspan="2"><?php esc_html_e( 'No scenarios found.', 'ug-ventsim' ); ?></td></tr>
                <?php endif; ?>
                </tbody>
            </table>
        </div>
        <?php
    }

    public function render_settings_page(): void {
        if ( ! current_user_can( 'manage_options' ) ) {
            return;
        }
        $settings = UVS_Settings::get_settings();
        ?>
        <div class="wrap">
            <h1><?php esc_html_e( 'UG VentSim Settings', 'ug-ventsim' ); ?></h1>
            <form method="post" action="options.php">
                <?php
                settings_fields( 'ug_ventsim_settings_group' );
                ?>
                <table class="form-table">
                    <tr>
                        <th><label for="unit_system"><?php esc_html_e( 'Unit System', 'ug-ventsim' ); ?></label></th>
                        <td>
                            <select name="uvs_settings[unit_system]" id="unit_system">
                                <option value="si" <?php selected( $settings['unit_system'], 'si' ); ?>><?php esc_html_e( 'SI (m³/s)', 'ug-ventsim' ); ?></option>
                                <option value="imperial" <?php selected( $settings['unit_system'], 'imperial' ); ?>><?php esc_html_e( 'Imperial (cfm)', 'ug-ventsim' ); ?></option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th><?php esc_html_e( 'Educational Mode', 'ug-ventsim' ); ?></th>
                        <td>
                            <label>
                                <input type="checkbox" name="uvs_settings[educational_mode]" value="1" <?php checked( $settings['educational_mode'], 1 ); ?>>
                                <?php esc_html_e( 'Show explanatory hints in widget output', 'ug-ventsim' ); ?>
                            </label>
                        </td>
                    </tr>
                    <tr>
                        <th><?php esc_html_e( 'Show Heat Load Panel', 'ug-ventsim' ); ?></th>
                        <td>
                            <label>
                                <input type="checkbox" name="uvs_settings[show_heat_load]" value="1" <?php checked( $settings['show_heat_load'], 1 ); ?>>
                                <?php esc_html_e( 'Display total heat load in frontend widget', 'ug-ventsim' ); ?>
                            </label>
                        </td>
                    </tr>
                    <tr>
                        <th><label for="min_velocity"><?php esc_html_e( 'Default Min Velocity (m/s)', 'ug-ventsim' ); ?></label></th>
                        <td>
                            <input type="number" step="0.01" min="0" name="uvs_settings[min_velocity]" id="min_velocity" value="<?php echo esc_attr( $settings['min_velocity'] ); ?>">
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
}
