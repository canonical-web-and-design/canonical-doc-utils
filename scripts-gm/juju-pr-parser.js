// Google App Script
// Scans Juju Github notification emails in Gmail labelled with 'git juju/core'
// and extracts Documentation Changes, placing them into a GDrive spreadsheet.

// TODO: split into functions

function myFuction(){

  var ss = SpreadsheetApp.openById(PLACE-SPREADSHEET-ID-HERE);
  var ss = ss.getSheetByName("Merges");

  // Grab unread threads with specific label
  var threads = GmailApp.search("label: 'git juju/core' is:unread");

  // Look for threads where documentation is required
  for (var t in threads) {
    
    var thread = threads[t];

    // Get message details for first message in thread
    var mesg = thread.getMessages()[0].getPlainBody();
    
    // Search to see if there's a doc changes section
    var start_match = mesg.match(/(Documentation changes)/gi);
    
    if (start_match != null){
    
      // extract doc changes
      var firstIndex = mesg.indexOf(start_match[0]);
      firstIndex = firstIndex + 21;
      // TODO: this needs smartening up, as bug reference could appear before doc changes
      var end_match = mesg.match(/(Bug reference|You can view, comment on, or merge this pull request)/gi);
      
      if (end_match != null){
        var lastIndex = mesg.indexOf(end_match[0], firstIndex);
        lastIndex = lastIndex - 3;
      } else {
        var lastIndex = mesg.length; 
      }
      
      var foundText = mesg.substring(firstIndex, lastIndex);
      
        // strip line breaks from the document changes description
      foundText = foundText.replace(/(\r\n|\n|\r)/gm, "");
  
      // check whether text is an excuse
      var doc_exempt = foundText.match(/^(N\/A|No|N.A.|NA|None|None.|\n|^$|Does it affect current user workflow\? CLI\? API\?|Does it affect current user workflow\? No  CLI\? No  API\? No|> Does it affect current user workflow\? CLI? API\?No.)/i);
      
      if (doc_exempt == null){
      
        // format date
        var subj = thread.getMessages()[0].getSubject();
        var date = Utilities.formatDate(thread.getMessages()[0].getDate(),"GMT","yyyy-MM-dd");
  
        // Extract the merge number from the subject
        // TODO: needs tuning - currently only looks/extracts 4 digit issue nos. like this: (#1234)
        var issue_raw = subj.match(/(\(#)(?:\d{4})(\))/g);
        
        if (issue_raw != null){
          
          var issue = issue_raw[0].match(/(?:\d{4})/g) || ['Not valid'];
    
          // Add a hyperlink to the issue number
          var url = "https://github.com/juju/juju/pull/";
          var formula = '=HYPERLINK("' + url + issue +'", "' + issue[0] + '")';
        } else {
         var formula = "Not found" 
        }
        
        // look for duplicates and only add new row if none are found
        var data=ss.getDataRange().getValues();
        var duplicate = false;
        
        var rows;
        
        for(i in data){
          
          if(data[i][1] == issue[0]){
            duplicate = true;
          } 
        }
        
        if (!duplicate)
          ss.appendRow([date, formula, "", subj, foundText]);
      } 
    }
    // mark thread as unread
    GmailApp.markThreadRead(thread);
  }
  
  // sort sheet after updates
  var range = ss.getDataRange();
  
  range.sort( {
    column: 2,
    ascending: false
  } );
   
}

