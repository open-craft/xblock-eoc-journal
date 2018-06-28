/* Javascript loaded in the learner view of the EOC Journal */

$(document).ready(function() {
    // Attach Google Analytics tracking to a set of events
    var ga = window[window['GoogleAnalyticsObject'] || 'ga'];
    if (typeof ga == 'function') {
        $('a.pdf-report-link').click(function() {
            ga('send', 'event', 'xblock-eoc-journal', 'click', 'PDF Report Download');
        });
        $('a.key-takeaways-link').click(function() {
            ga('send', 'event', 'xblock-eoc-journal', 'click', 'Key Takeaways PDF Download');
        });
    }
});
