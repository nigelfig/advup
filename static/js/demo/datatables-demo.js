// Call the dataTables jQuery plugin
$(document).ready(function() {
  
  // | date:'M j, Y g:m A'
  $.fn.dataTable.moment( 'MMM D, YYYY h:mm:ss A' );
  $('#dataTable').DataTable( {
    "order": [[ 4, "desc" ]]
  } );
});

