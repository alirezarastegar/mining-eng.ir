/**
 * UG-VentSim Admin JavaScript
 */

(function($) {
    'use strict';

    const UGVentSimAdmin = {
        ajaxUrl: window.ugvAdmin?.ajaxUrl || '',
        nonce: window.ugvAdmin?.nonce || '',

        /**
         * Delete equipment
         */
        deleteEquipment: function(equipmentId) {
            if (!confirm(window.ugvAdmin?.i18n?.confirm_delete || 'آیا مطمئن هستید؟')) {
                return;
            }

            $.ajax({
                url: this.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'uvs_delete_equipment',
                    equipment_id: equipmentId,
                    nonce: this.nonce
                },
                success: function(response) {
                    if (response.success) {
                        alert(window.ugvAdmin?.i18n?.saved || 'حذف شد!');
                        location.reload();
                    } else {
                        alert(response.data || window.ugvAdmin?.i18n?.error || 'خطا');
                    }
                },
                error: function() {
                    alert(window.ugvAdmin?.i18n?.error || 'خطا');
                }
            });
        },

        /**
         * Duplicate scenario
         */
        duplicateScenario: function(scenarioId) {
            const newTitle = prompt('نام جدید سناریو:', 'Duplicated Scenario');
            if (!newTitle) return;

            $.ajax({
                url: this.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'uvs_duplicate_scenario',
                    scenario_id: scenarioId,
                    new_title: newTitle,
                    nonce: this.nonce
                },
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert('خطا در کپی کردن');
                    }
                }
            });
        },

        /**
         * Export scenarios
         */
        exportScenarios: function() {
            $.ajax({
                url: this.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'uvs_export_scenarios',
                    nonce: this.nonce
                },
                success: function(response) {
                    if (response.success) {
                        // File will be downloaded
                        window.location.href = response.data.url;
                    }
                }
            });
        },

        /**
         * Initialize
         */
        init: function() {
            // Delete equipment button
            $(document).on('click', '.ugv-delete-equipment-btn', function(e) {
                e.preventDefault();
                const equipmentId = $(this).data('equipment-id');
                UGVentSimAdmin.deleteEquipment(equipmentId);
            });

            // Duplicate scenario button
            $(document).on('click', '.ugv-duplicate-scenario-btn', function(e) {
                e.preventDefault();
                const scenarioId = $(this).data('scenario-id');
                UGVentSimAdmin.duplicateScenario(scenarioId);
            });

            // Export button
            $(document).on('click', '#ugv-export-scenarios-btn', function(e) {
                e.preventDefault();
                UGVentSimAdmin.exportScenarios();
            });

            console.log('UGVentSim Admin initialized');
        }
    };

    // Global functions
    window.uvgDeleteEquipment = function(id) {
        UGVentSimAdmin.deleteEquipment(id);
    };

    window.ugvDuplicateScenario = function(id) {
        UGVentSimAdmin.duplicateScenario(id);
    };

    window.ugvExportScenarios = function() {
        UGVentSimAdmin.exportScenarios();
    };

    // Initialize
    $(document).ready(function() {
        UGVentSimAdmin.init();
    });

})(jQuery);