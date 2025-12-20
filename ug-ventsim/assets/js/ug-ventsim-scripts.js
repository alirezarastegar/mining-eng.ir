/**
 * UG-VentSim Frontend JavaScript
 */

jQuery(document).ready(function ($) {
    'use strict';

    const UGVentSim = {
        ajaxUrl: window.ugvFrontend?.ajaxUrl || '',
        nonce: window.ugvFrontend?.nonce || '',

        /**
         * Save scenario from widget
         */
        saveScenario: function(title, data) {
            $.ajax({
                url: this.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'uvs_save_scenario',
                    title: title,
                    data: JSON.stringify(data),
                    nonce: this.nonce
                },
                success: function(response) {
                    if (response.success) {
                        alert('سناریو با موفقیت ذخیره شد! ID: ' + response.data.scenario_id);
                    } else {
                        alert('خطا در ذخیره سناریو');
                    }
                },
                error: function() {
                    alert('خطای سرور');
                }
            });
        },

        /**
         * Bar chart rendering
         */
        renderCharts: function() {
            $('.ugv-bar-chart').each(function() {
                const $chart = $(this);
                const vals = [
                    parseFloat($chart.data('q-velocity')) || 0,
                    parseFloat($chart.data('q-personnel')) || 0,
                    parseFloat($chart.data('q-gas')) || 0,
                    parseFloat($chart.data('q-diesel')) || 0,
                    parseFloat($chart.data('q-heat')) || 0
                ];

                const max = Math.max.apply(null, vals) || 1;

                $chart.find('.ugv-bar').each(function(index) {
                    const v = vals[index];
                    const h = (v / max) * 100;
                    $(this).css('height', Math.max(h, 4) + '%');
                });
            });
        },

        /**
         * Initialize
         */
        init: function() {
            this.renderCharts();

            // Save scenario button
            $(document).on('click', '.ugv-save-scenario-btn', function(e) {
                e.preventDefault();
                const title = prompt('عنوان سناریو:', 'New Scenario');
                if (title) {
                    const data = $(this).closest('.ugv-widget').data('scenario-data') || {};
                    UGVentSim.saveScenario(title, data);
                }
            });

            // Print button
            $(document).on('click', '.ugv-print-btn', function(e) {
                e.preventDefault();
                window.print();
            });

            console.log('UGVentSim Frontend initialized');
        }
    };

    // Global function
    window.ugvSaveScenario = function(title, data) {
        UGVentSim.saveScenario(title, data);
    };

    // Initialize
    UGVentSim.init();

});