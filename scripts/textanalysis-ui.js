var text = ""; // Last text of sentence
var sugg = []; // suggestions for autocompletion of node names

$('#textanalyser').autocompleteTrigger({
    triggerStart: '#',
    triggerEnd: '',
    source: sugg
});

function analyzeSentence(sentence, finalize)
{
    var d = TextAnalyser2(graph, sentence, finalize);
    for (var k in d.suggestions) {
        sugg[k] = k;
    }
}


$("#textanalyser").keypress(function(e) {
     if (graph.history !== undefined) {
         graph.history.record_keystrokes(KEYSTROKE_WHERE_TEXTANALYSIS, [e.which]);
     }
     if (e.which == 13) {
        if(!suggestionChange){
            text = $('#textanalyser').val();
            $('#textanalyser').val("");
            TextAnalyser2(graph, text, true);
            typeStack=[];
        } else {
            suggestionChange=false;
        }
        return false;
    }

    if (e.which == 37) {//RIGHT
        $('body').scrollLeft(0);
        e.stopPropagation();
        return false;
    }
    if (e.which == 39) { //LEFT
        $('body').scrollLeft(0);
        e.stopPropagation();
        return false;
    }

});

$(document).keydown(function(e) {
  
    if (graph.history !== undefined) {
        graph.history.record_keystrokes(KEYSTROKE_WHERE_DOCUMENT, [e.KeyCode]);
    }
    if (e.keyCode == 9) {//TAB
        e.preventDefault();
        changeType("down", lastnode);
        return false;
    }

    if (e.keyCode == 37) {//UP
          $('html, body').scrollLeft(0);
    }
    if (e.keyCode == 39) {//DOWN
          $('html, body').scrollLeft(0);
    }

    if (e.keyCode == 38) {//UP
        suggestionChange=true;
    }
    if (e.keyCode == 40) {//DOWN
        suggestionChange=true;
    }

    if (e.keyCode == 9) {//TAB
        return false;
    }

});

function textSelect(inp, s, e) {
    e = e || s;
    if (inp.createTextRange) {
        var r = inp.createTextRange();
        r.collapse(true);
        r.moveEnd('character', e);
        r.moveStart('character', s);
        r.select();
    }else if(inp.setSelectionRange) {
        inp.focus();
        inp.setSelectionRange(s, e);
    }
}

function changeType(arg, id) {
    if(!id)id="new node";
    if (arg === 'up') {
        if (typeindex < 4) typeindex++;
        else typeindex = 0;
        graph.editType(id, null, nodetypes[typeindex]);
        $('.typeselection').html('<table><tr><td style="height:28px"></td></tr><tr><td>' + "Chosen Type: " + nodetypes[typeindex] + '</td></tr></table>');
        graph.findCoordinates(lastnode,null);
    } else {
        if (typeindex > 0) typeindex--;
        else typeindex = 4;

        graph.editType(id, null, nodetypes[typeindex]);
        $('.typeselection').html('<table><tr><td style="height:28px"></td></tr><tr><td>' + "Chosen Type: " + nodetypes[typeindex] + '</td></tr></table>');
        graph.findCoordinates(lastnode,null);

    }
    graph.updateGraph();
}

window.setInterval(function() {
    if ($('#textanalyser').val() != text) {

        if(text.length*8>500)$('#textanalyser').css('width',text.length*8+20);
        // text changed
        text = $('#textanalyser').val();
        TextAnalyser2(graph, text, false);
        suggestionChange=false;
    }
}, 5);


