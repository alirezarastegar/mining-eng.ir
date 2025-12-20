<?php
/**
 * Equipment Form View
 *
 * @var array|null $editing_item  ردیف تجهیز برای ویرایش (یا null برای افزودن جدید)
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

$is_edit = ! empty( $editing_item ) && ! empty( $editing_item['id'] );
?>
<div class="wrap ugv-wrap">
    <h1 class="ugv-page-title">
        <?php echo $is_edit
            ? esc_html__( 'Edit Equipment', 'ug-ventsim' )
            : esc_html__( 'Add Diesel Equipment', 'ug-ventsim' ); ?>
    </h1>

    <div class="ugv-card">
        <form method="post">
            <?php wp_nonce_field( 'ugv_equipment_save', 'ugv_equipment_nonce' ); ?>

            <?php if ( $is_edit ) : ?>
                <input type="hidden" name="id" value="<?php echo esc_attr( $editing_item['id'] ); ?>">
            <?php endif; ?>

            <table class="form-table">
                <tr>
                    <th><label for="model_name"><?php esc_html_e( 'Model Name', 'ug-ventsim' ); ?></label></th>
                    <td>
                        <input type="text" name="model_name" id="model_name" class="regular-text"
                               value="<?php echo esc_attr( $editing_item['model_name'] ?? '' ); ?>" required>
                    </td>
                </tr>
                <tr>
                    <th><label for="type"><?php esc_html_e( 'Type', 'ug-ventsim' ); ?></label></th>
                    <td>
                        <input type="text" name="type" id="type" class="regular-text"
                               value="<?php echo esc_attr( $editing_item['type'] ?? '' ); ?>" required>
                    </td>
                </tr>
                <tr>
                    <th><label for="manufacturer"><?php esc_html_e( 'Manufacturer', 'ug-ventsim' ); ?></label></th>
                    <td>
                        <input type="text" name="manufacturer" id="manufacturer" class="regular-text"
                               value="<?php echo esc_attr( $editing_item['manufacturer'] ?? '' ); ?>">
                    </td>
                </tr>
                <tr>
                    <th><label for="engine_power_kw"><?php esc_html_e( 'Engine Power (kW)', 'ug-ventsim' ); ?></label></th>
                    <td>
                        <input type="number" step="0.1" name="engine_power_kw" id="engine_power_kw"
                               value="<?php echo esc_attr( $editing_item['engine_power_kw'] ?? '' ); ?>" required>
                    </td>
                </tr>
                <tr>
                    <th><label for="ventilation_rate_factor"><?php esc_html_e( 'Ventilation Factor (m³/s per kW)', 'ug-ventsim' ); ?></label></th>
                    <td>
                        <input type="number" step="0.001" name="ventilation_rate_factor" id="ventilation_rate_factor"
                               value="<?php echo esc_attr( $editing_item['ventilation_rate_factor'] ?? '' ); ?>" required>
                    </td>
                </tr>
                <tr>
                    <th><label for="exhaust_volume_cfm"><?php esc_html_e( 'Exhaust Volume (cfm)', 'ug-ventsim' ); ?></label></th>
                    <td>
                        <input type="number" step="0.1" name="exhaust_volume_cfm" id="exhaust_volume_cfm"
                               value="<?php echo esc_attr( $editing_item['exhaust_volume_cfm'] ?? '' ); ?>">
                    </td>
                </tr>
            </table>

            <?php
            submit_button(
                $is_edit
                    ? __( 'Update Equipment', 'ug-ventsim' )
                    : __( 'Add Equipment', 'ug-ventsim' )
            );
            ?>
        </form>
    </div>
</div>
