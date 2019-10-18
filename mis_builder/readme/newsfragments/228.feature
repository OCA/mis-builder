Support analytic tag filters in the backend view and preview widget.
Selecting several tags in the filter means filtering on move lines which
have *all* these tags set. This is to support the most common use case of
using tags for different dimensions. The filter also makes a AND with the
analytic account filter.