<?php
namespace UGVentSim\Core;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class UVS_Settings {

    const OPTION_KEY = 'uvs_settings';

    /**
     * Boot
     */
    public function __construct() {
        add_action( 'admin_init', [ $this, 'register_settings' ] );
    }

    /**
     * Default settings
     *
     * @return array
     */
    public static function defaults(): array {
        return [
            'unit_system'      => 'si',   // si | imperial
            'educational_mode' => 1,
            'show_heat_load'   => 1,
            'min_velocity'     => 0.25,
        ];
    }

    /**
     * Get merged settings
     *
     * @return array
     */
    public static function get_settings(): array {
        $saved = get_option( self::OPTION_KEY, [] );

        if ( ! is_array( $saved ) ) {
            $saved = [];
        }

        return array_merge( self::defaults(), $saved );
    }

    /**
     * Update settings
     *
     * @param array $data
     * @return bool
     */
    public static function update_settings( array $data ): bool {
        $settings = self::get_settings();

        $settings['unit_system']      = in_array( $data['unit_system'] ?? 'si', [ 'si', 'imperial' ], true ) ? $data['unit_system'] : 'si';
        $settings['educational_mode'] = ! empty( $data['educational_mode'] ) ? 1 : 0;
        $settings['show_heat_load']   = ! empty( $data['show_heat_load'] ) ? 1 : 0;
        $settings['min_velocity']     = isset( $data['min_velocity'] ) ? (float) $data['min_velocity'] : $settings['min_velocity'];

        return update_option( self::OPTION_KEY, $settings );
    }

    /**
     * Register with Settings API (for future use in admin page)
     */
    public function register_settings() {
        register_setting(
            'ug_ventsim_settings_group',
            self::OPTION_KEY,
            [ __CLASS__, 'sanitize_callback' ]
        );

        add_settings_section(
            'ug_ventsim_main_section',
            __( 'UG-VentSim Global Settings', 'ug-ventsim' ),
            function () {
                echo '<p>' . esc_html__( 'Configure default behavior of the ventilation simulator.', 'ug-ventsim' ) . '</p>';
            },
            'ug-ventsim-settings'
        );

        add_settings_field(
            'uvs_unit_system',
            __( 'Default Unit System', 'ug-ventsim' ),
            [ $this, 'field_unit_system' ],
            'ug-ventsim-settings',
            'ug_ventsim_main_section'
        );

        add_settings_field(
            'uvs_educational_mode',
            __( 'Educational Mode', 'ug-ventsim' ),
            [ $this, 'field_educational_mode' ],
            'ug-ventsim-settings',
            'ug_ventsim_main_section'
        );

        add_settings_field(
            'uvs_show_heat_load',
            __( 'Show Heat Load Panel', 'ug-ventsim' ),
            [ $this, 'field_show_heat_load' ],
            'ug-ventsim-settings',
            'ug_ventsim_main_section'
        );

        add_settings_field(
            'uvs_min_velocity',
            __( 'Default Minimum Velocity (m/s)', 'ug-ventsim' ),
            [ $this, 'field_min_velocity' ],
            'ug-ventsim-settings',
            'ug_ventsim_main_section'
        );
    }

    /**
     * Sanitize callback
     *
     * @param array $input
     * @return array
     */
    public static function sanitize_callback( $input ): array {
        if ( ! is_array( $input ) ) {
            $input = [];
        }

        return [
            'unit_system'      => in_array( $input['unit_system'] ?? 'si', [ 'si', 'imperial' ], true ) ? $input['unit_system'] : 'si',
            'educational_mode' => ! empty( $input['educational_mode'] ) ? 1 : 0,
            'show_heat_load'   => ! empty( $input['show_heat_load'] ) ? 1 : 0,
            'min_velocity'     => isset( $input['min_velocity'] ) ? (float) $input['min_velocity'] : 0.25,
        ];
    }

    public function field_unit_system() {
        $settings = self::get_settings();
        ?>
        <select name="<?php echo esc_attr( self::OPTION_KEY ); ?>[unit_system]">
            <option value="si" <?php selected( $settings['unit_system'], 'si' ); ?>><?php esc_html_e( 'SI (m³/s, kW)', 'ug-ventsim' ); ?></option>
            <option value="imperial" <?php selected( $settings['unit_system'], 'imperial' ); ?>><?php esc_html_e( 'Imperial (cfm, BTU/h)', 'ug-ventsim' ); ?></option>
        </select>
        <?php
    }

    public function field_educational_mode() {
        $settings = self::get_settings();
        ?>
        <label>
            <input type="checkbox" name="<?php echo esc_attr( self::OPTION_KEY ); ?>[educational_mode]" value="1" <?php checked( $settings['educational_mode'], 1 ); ?>>
            <?php esc_html_e( 'Show explanations and factor breakdown for teaching', 'ug-ventsim' ); ?>
        </label>
        <?php
    }

    public function field_show_heat_load() {
        $settings = self::get_settings();
        ?>
        <label>
            <input type="checkbox" name="<?php echo esc_attr( self::OPTION_KEY ); ?>[show_heat_load]" value="1" <?php checked( $settings['show_heat_load'], 1 ); ?>>
            <?php esc_html_e( 'Display total heat load panel in frontend widget', 'ug-ventsim' ); ?>
        </label>
        <?php
    }

    public function field_min_velocity() {
        $settings = self::get_settings();
        ?>
        <input type="number" step="0.01" min="0" name="<?php echo esc_attr( self::OPTION_KEY ); ?>[min_velocity]" value="<?php echo esc_attr( $settings['min_velocity'] ); ?>">
        <p class="description"><?php esc_html_e( 'Default minimum airway velocity used if not overridden by scenario/widget.', 'ug-ventsim' ); ?></p>
        <?php
    }
}