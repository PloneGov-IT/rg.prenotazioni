/*globals jQuery, document*/
/*jslint sloppy: true, vars: true, white: true, maxerr: 50, indent: 4 */
/*
 * This is the javascript that looks for overlays
 */
(function ($) {
    /*
    * Apply an overlay to all the links with class infoIco like
    */
    function prepOverlay() {
        return $('a.prenotazioni-popup').prepOverlay({
            subtype: 'ajax',
        });
    }
    jq(document).ready(prepOverlay);
}(jQuery));
