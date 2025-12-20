<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
?>
<div class="wrap">
    <h1><?php esc_html_e( 'UG-VentSim Dashboard', 'ug-ventsim' ); ?></h1>
    
    <div class="ugv-dashboard-stats">
        <div class="stat-box">
            <h3><?php esc_html_e( 'Total Equipment', 'ug-ventsim' ); ?></h3>
            <p class="stat-number"><?php echo esc_html( $total_equipment ); ?></p>
        </div>
        <div class="stat-box">
            <h3><?php esc_html_e( 'Saved Scenarios', 'ug-ventsim' ); ?></h3>
            <p class="stat-number"><?php echo esc_html( $total_scenarios ); ?></p>
        </div>
    </div>
    
    <div class="ugv-quick-links">
        <a href="<?php echo esc_url( admin_url( 'admin.php?page=ug-ventsim-equipment' ) ); ?>" class="button button-primary">
            <?php esc_html_e( 'Manage Equipment', 'ug-ventsim' ); ?>
        </a>
        <a href="<?php echo esc_url( admin_url( 'admin.php?page=ug-ventsim-scenarios' ) ); ?>" class="button button-primary">
            <?php esc_html_e( 'View Scenarios', 'ug-ventsim' ); ?>
        </a>
        <a href="<?php echo esc_url( admin_url( 'admin.php?page=ug-ventsim-settings' ) ); ?>" class="button button-primary">
            <?php esc_html_e( 'Settings', 'ug-ventsim' ); ?>
        </a>
    </div>
</div>
