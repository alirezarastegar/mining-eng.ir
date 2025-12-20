<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
?>
<div class="wrap">
    <h1><?php esc_html_e( 'Equipment Library', 'ug-ventsim' ); ?></h1>
    
    <?php if ( $edit_item ) : ?>
        <h2><?php esc_html_e( 'Edit Equipment', 'ug-ventsim' ); ?></h2>
    <?php else : ?>
        <h2><?php esc_html_e( 'Add New Equipment', 'ug-ventsim' ); ?></h2>
    <?php endif; ?>
    
    <form method="post" class="ugv-equipment-form">
        <?php wp_nonce_field( 'ugv_equipment_save', 'ugv_equipment_nonce' ); ?>
        
        <?php if ( $edit_item ) : ?>
            <input type="hidden" name="equipment_id" value="<?php echo esc_attr( $edit_item['id'] ); ?>">
        <?php endif; ?>
        
        <table class="form-table">
            <tr>
                <th><label for="model_name"><?php esc_html_e( 'Model Name', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="text" id="model_name" name="model_name" 
                           value="<?php echo esc_attr( $edit_item['model_name'] ?? '' ); ?>" required>
                </td>
            </tr>
            <tr>
                <th><label for="type"><?php esc_html_e( 'Equipment Type', 'ug-ventsim' ); ?></label></th>
                <td>
                    <select id="type" name="type" required>
                        <option value=""><?php esc_html_e( '— Select Type —', 'ug-ventsim' ); ?></option>
                        <option value="LHD" <?php selected( $edit_item['type'] ?? '', 'LHD' ); ?>>LHD</option>
                        <option value="Truck" <?php selected( $edit_item['type'] ?? '', 'Truck' ); ?>>Truck</option>
                        <option value="Jumbo Drill" <?php selected( $edit_item['type'] ?? '', 'Jumbo Drill' ); ?>>Jumbo Drill</option>
                    </select>
                </td>
            </tr>
            <tr>
                <th><label for="manufacturer"><?php esc_html_e( 'Manufacturer', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="text" id="manufacturer" name="manufacturer" 
                           value="<?php echo esc_attr( $edit_item['manufacturer'] ?? '' ); ?>">
                </td>
            </tr>
            <tr>
                <th><label for="engine_power_kw"><?php esc_html_e( 'Engine Power (kW)', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="number" id="engine_power_kw" name="engine_power_kw" step="0.1"
                           value="<?php echo esc_attr( $edit_item['engine_power_kw'] ?? '' ); ?>" required>
                </td>
            </tr>
            <tr>
                <th><label for="ventilation_rate_factor"><?php esc_html_e( 'Ventilation Rate Factor', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="number" id="ventilation_rate_factor" name="ventilation_rate_factor" step="0.001"
                           value="<?php echo esc_attr( $edit_item['ventilation_rate_factor'] ?? '' ); ?>" required>
                </td>
            </tr>
            <tr>
                <th><label for="exhaust_volume_cfm"><?php esc_html_e( 'Exhaust Volume (CFM)', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="number" id="exhaust_volume_cfm" name="exhaust_volume_cfm" step="0.1"
                           value="<?php echo esc_attr( $edit_item['exhaust_volume_cfm'] ?? '' ); ?>">
                </td>
            </tr>
            <tr>
                <th><label for="heat_output_kw"><?php esc_html_e( 'Heat Output (kW)', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="number" id="heat_output_kw" name="heat_output_kw" step="0.1"
                           value="<?php echo esc_attr( $edit_item['heat_output_kw'] ?? '' ); ?>">
                </td>
            </tr>
            <tr>
                <th><label for="dpm_factor"><?php esc_html_e( 'DPM Factor', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="number" id="dpm_factor" name="dpm_factor" step="0.01"
                           value="<?php echo esc_attr( $edit_item['dpm_factor'] ?? '' ); ?>">
                </td>
            </tr>
            <tr>
                <th><label for="engine_class"><?php esc_html_e( 'Engine Class', 'ug-ventsim' ); ?></label></th>
                <td>
                    <input type="text" id="engine_class" name="engine_class" 
                           value="<?php echo esc_attr( $edit_item['engine_class'] ?? '' ); ?>">
                </td>
            </tr>
            <tr>
                <th><label for="notes"><?php esc_html_e( 'Notes', 'ug-ventsim' ); ?></label></th>
                <td>
                    <textarea id="notes" name="notes" rows="4"><?php echo esc_textarea( $edit_item['notes'] ?? '' ); ?></textarea>
                </td>
            </tr>
        </table>
        
        <?php submit_button( $edit_item ? __( 'Update Equipment', 'ug-ventsim' ) : __( 'Add Equipment', 'ug-ventsim' ) ); ?>
    </form>
    
    <h2><?php esc_html_e( 'Existing Equipment', 'ug-ventsim' ); ?></h2>
    <table class="widefat striped">
        <thead>
            <tr>
                <th><?php esc_html_e( 'Model', 'ug-ventsim' ); ?></th>
                <th><?php esc_html_e( 'Type', 'ug-ventsim' ); ?></th>
                <th><?php esc_html_e( 'Manufacturer', 'ug-ventsim' ); ?></th>
                <th><?php esc_html_e( 'Power (kW)', 'ug-ventsim' ); ?></th>
                <th><?php esc_html_e( 'Actions', 'ug-ventsim' ); ?></th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ( $equipment as $item ) : ?>
                <tr>
                    <td><?php echo esc_html( $item['model_name'] ); ?></td>
                    <td><?php echo esc_html( $item['type'] ); ?></td>
                    <td><?php echo esc_html( $item['manufacturer'] ); ?></td>
                    <td><?php echo esc_html( $item['engine_power_kw'] ); ?></td>
                    <td>
                        <a href="<?php echo esc_url( admin_url( 'admin.php?page=ug-ventsim-equipment&edit=' . $item['id'] ) ); ?>" class="button button-small">
                            <?php esc_html_e( 'Edit', 'ug-ventsim' ); ?>
                        </a>
                        <button class="button button-small button-link-delete" onclick="uvgDeleteEquipment(<?php echo intval( $item['id'] ); ?>)">
                            <?php esc_html_e( 'Delete', 'ug-ventsim' ); ?>
                        </button>
                    </td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>