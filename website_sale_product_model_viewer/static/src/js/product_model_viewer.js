odoo.define('website_sale_product_model_viewer', function(require) {
    'use strict';
    require('web.core');

    $(document).ready(function () {
        var $fullscreen_button = $('#product-3d-model-viewer-fullscreen');
        $fullscreen_button.click(function (ev) {
            var isFullscreenAvailable = document.fullscreenEnabled || document.mozFullScreenEnabled || document.webkitFullscreenEnabled || document.msFullscreenEnabled || false;
            var modelViewerElem = ev.target.parentElement.parentElement.parentElement;
            if (isFullscreenAvailable) {
                var fullscreenElement = document.fullscreenElement || document.mozFullScreenElement || document.webkitFullscreenElement || document.msFullscreenElement;
                if (fullscreenElement) {
                  if (document.exitFullscreen) {
                    document.exitFullscreen();
                  } else if (document.mozCancelFullScreen) { /* Firefox */
                    document.mozCancelFullScreen();
                  } else if (document.webkitExitFullscreen) { /* Chrome, Safari and Opera */
                    document.webkitExitFullscreen();
                  } else if (document.msExitFullscreen) { /* IE/Edge */
                    document.msExitFullscreen();
                  }
                }
                else {
                    if (modelViewerElem.requestFullscreen) {
                      modelViewerElem.requestFullscreen();
                    } else if (modelViewerElem.mozRequestFullScreen) { /* Firefox */
                       modelViewerElem.mozRequestFullScreen();
                    } else if (modelViewerElem.webkitRequestFullscreen) { /* Chrome, Safari and Opera */
                       modelViewerElem.webkitRequestFullscreen();
                    } else if (modelViewerElem.msRequestFullscreen) { /* IE/Edge */
                       modelViewerElem.msRequestFullscreen();
                    }
                }
            }
            else {
                console.error("ERROR : full screen not supported by web browser");
            }
        });

    });
});
