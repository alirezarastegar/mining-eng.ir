<?php
/**
 * Scenarios Page Template
 * 
 * Displays all saved ventilation scenarios with full management options
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
?>

<div class="wrap">
    <h1><?php esc_html_e( 'Ventilation Scenarios', 'ug-ventsim' ); ?></h1>
    
    <div class="ugv-scenarios-toolbar">
        <button class="button button-primary" id="export-scenarios-btn">
            <?php esc_html_e( 'Export CSV', 'ug-ventsim' ); ?>
        </button>
        <button class="button" id="import-scenarios-btn">
            <?php esc_html_e( 'Import CSV', 'ug-ventsim' ); ?>
        </button>
    </div>
    
    <table class="widefat striped">
        <thead>
            <tr>
                <th><?php esc_html_e( 'ID', 'ug-ventsim' ); ?></th>
                <th><?php esc_html_e( 'Title', 'ug-ventsim' ); ?></th>
                <th><?php esc_html_e( 'Description', 'ug-ventsim' ); ?></th>
                <th><?php esc_html_e( 'Date Created', 'ug-ventsim' ); ?></th>
                <th><?php esc_html_e( 'Actions', 'ug-ventsim' ); ?></th>
            </tr>
        </thead>
        <tbody>
            <?php if ( ! empty( $scenarios ) ) : ?>
                <?php foreach ( $scenarios as $scenario ) : ?>
                    <tr>
                        <td><?php echo esc_html( $scenario['id'] ); ?></td>
                        <td><strong><?php echo esc_html( $scenario['title'] ); ?></strong></td>
                        <td><?php echo esc_html( wp_trim_words( $scenario['description'], 15 ) ); ?></td>
                        <td><?php echo esc_html( mysql2date( get_option( 'date_format' ), $scenario['date'] ) ); ?></td>
                        <td>
                            <a href="<?php echo esc_url( admin_url( 'post.php?action=edit&post=' . $scenario['id'] ) ); ?>" class="button button-small">
                                <?php esc_html_e( 'Edit', 'ug-ventsim' ); ?>
                            </a>
                            <button class="button button-small button-link-delete" 
                                    onclick="uvgDuplicateScenario(<?php echo intval( $scenario['id'] ); ?>)">
                                <?php esc_html_e( 'Duplicate', 'ug-ventsim' ); ?>
                            </button>
                            <a href="<?php echo esc_url( wp_nonce_url( admin_url( 'admin.php?page=ug-ventsim-scenarios&action=delete&scenario_id=' . $scenario['id'] ), 'uvs_scenario_action' ) ); ?>" class="button button-small button-link-delete" onclick="return confirm('<?php esc_attr_e( 'Delete this scenario permanently?', 'ug-ventsim' ); ?>')">
                                <?php esc_html_e( 'Delete', 'ug-ventsim' ); ?>
                            </a>
                        </td>
                    </tr>
                <?php endforeach; ?>
            <?php else : ?>
                <tr>
                    <td colspan="5" style="text-align: center; padding: 30px;">
                        <?php esc_html_e( 'No scenarios found. Create one from the Elementor widget!', 'ug-ventsim' ); ?>
                    </td>
                </tr>
            <?php endif; ?>
        </tbody>
    </table>
    
    <div class="ugv-scenarios-footer" style="margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px;">
        <p style="color: #666;">
            <strong><?php esc_html_e( 'Tip:', 'ug-ventsim' ); ?></strong>
            <?php esc_html_e( 'Scenarios are created when you save calculations from the Elementor widget. You can edit, duplicate, or export them here.', 'ug-ventsim' ); ?>
        </p>
    </div>
</div>

<script>
    function uvgDuplicateScenario(scenarioId) {
        const newTitle = prompt('<?php esc_attr_e( 'Enter new scenario title:', 'ug-ventsim' ); ?>');
        if (newTitle) {
            jQuery.ajax({
                url: ugvAdmin.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'uvs_duplicate_scenario',
                    scenario_id: scenarioId,
                    new_title: newTitle,
                    nonce: ugvAdmin.nonce
                },
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.data.message || '<?php esc_attr_e( 'Error duplicating scenario', 'ug-ventsim' ); ?>');
                    }
                }
            });
        }
    }

    document.getElementById('export-scenarios-btn')?.addEventListener('click', function() {
        jQuery.ajax({
            url: ugvAdmin.ajaxUrl,
            type: 'POST',
            data: {
                action: 'uvs_export_scenarios',
                nonce: ugvAdmin.nonce
            }
        });
    });

    document.getElementById('import-scenarios-btn')?.addEventListener('click', function() {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.csv';
        fileInput.onchange = function(e) {
            const formData = new FormData();
            formData.append('action', 'uvs_import_scenarios');
            formData.append('nonce', ugvAdmin.nonce);
            formData.append('file', e.target.files[0]);

            jQuery.ajax({
                url: ugvAdmin.ajaxUrl,
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    }
                }
            });
        };
        fileInput.click();
    });
</script>