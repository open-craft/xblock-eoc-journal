/* Javascript loaded in the learner view of the Course Journal */

function EOCJournalXBlock(runtime, element) {
    // Attach Google Analytics tracking to a set of events
    var ga = window[window['GoogleAnalyticsObject'] || 'ga'];
    if (typeof ga == 'function') {
        $('a.pdf-report-link', element).click(function() {
            ga('send', 'event', 'Course Journal', 'click', 'PDF Report Download');
        });
        $('a.key-takeaways-link', element).click(function() {
            ga('send', 'event', 'Course Journal', 'click', 'Key Takeaways PDF Download');
        });
    }
}
