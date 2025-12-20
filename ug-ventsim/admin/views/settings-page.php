<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
?>
<div class="wrap">
    <h1><?php esc_html_e( 'UG-VentSim Settings', 'ug-ventsim' ); ?></h1>
    
    <form method="post" class="ugv-settings-form">
        <?php wp_nonce_field( 'uvs_settings_save', 'uvs_settings_nonce' ); ?>
        
        <table class="form-table">
            <tr>
                <th><label for="unit_system"><?php esc_html_e( 'Unit System', 'ug-ventsim' ); ?></label></th>
                <td>
                    <select id="unit_system" name="unit_system">
                        <option value="si" <?php selected( $settings['unit_system'] ?? 'si', 'si' ); ?>>SI (m³/s)</option>
                        <option value="imperial" <?php selected( $settings['unit_system'] ?? '', 'imperial' ); ?>>Imperial (CFM)</option>
                    </select>
                </td>
            </tr>
            <tr>
                <th><label for="standard_profile"><?php esc_html_e( 'Standard Profile', 'ug-ventsim' ); ?></label></th>
                <td>
                    <select id="standard_profile" name="standard_profile">
                        <option value="australian" <?php selected( $settings['standard_profile'] ?? 'australian', 'australian' ); ?>>Australian Standard</option>
                        <option value="canadian" <?php selected( $settings['standard_profile'] ?? '', 'canadian' ); ?>>Canadian Standard</option>
                        <option value="us" <?php selected( $settings['standard_profile'] ?? '', 'us' ); ?>>US Standard</option>
                    </select>
                </td>
            </tr>
            <tr>
                <th><label for="min_velocity_m"><?php esc_html_e( 'Minimum Velocity (m/s)', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="number" id="min_velocity_m" name="min_velocity_m" step="0.01" value="<?php echo esc_attr( $settings['min_velocity_m'] ?? 0.25 ); ?>">
                </td>
            </tr>
            <tr>
                <th><label for="air_density"><?php esc_html_e( 'Air Density (kg/m³)', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="number" id="air_density" name="air_density" step="0.1" value="<?php echo esc_attr( $settings['air_density'] ?? 1.2 ); ?>">
                </td>
            </tr>
            <tr>
                <th><label for="tlv_methane"><?php esc_html_e( 'TLV Methane (%)', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="number" id="tlv_methane" name="tlv_methane" step="0.01" value="<?php echo esc_attr( $settings['tlv_methane'] ?? 1.0 ); ?>">
                </td>
            </tr>
            <tr>
                <th><label for="tlv_co"><?php esc_html_e( 'TLV Carbon Monoxide (ppm)', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="number" id="tlv_co" name="tlv_co" step="0.01" value="<?php echo esc_attr( $settings['tlv_co'] ?? 0.1 ); ?>">
                </td>
            </tr>
            <tr>
                <th><label for="tlv_h2s"><?php esc_html_e( 'TLV Hydrogen Sulfide (ppm)', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="number" id="tlv_h2s" name="tlv_h2s" step="0.01" value="<?php echo esc_attr( $settings['tlv_h2s'] ?? 0.05 ); ?>">
                </td>
            </tr>
        </table>
        
        <?php submit_button(); ?>
    </form>
</div>
