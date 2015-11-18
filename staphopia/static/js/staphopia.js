/*
    results.html
*/
function show_panel(navbar_id) {
    panel_id = get_panel_id(navbar_id);
    $(panel_id).removeClass('hide')

    if (panel_id == '#mlst_related_panel') {
        var table = $('#mlst_related_table').DataTable();
        table.columns.adjust().draw();
    }
}

function hide_panel(navbar_id) {
    panel_id = get_panel_id(navbar_id);
    $(panel_id).addClass('hide')
}

function get_panel_id(navbar_id) {
    panel_id = ''
    switch(navbar_id) {
          case "show-meta-data":
            panel_id = '#meta-data_panel'
            break;
          case "show-phenotype":
            panel_id = '#phenotype_panel';
            break;
          case "show-sequence":
            panel_id = '#sequence_panel';
            break;
          case "show-assembly":
            panel_id = '#assembly_panel'
            break;
          case "show-mlst":
            panel_id = '#mlst_panel'
            break;
          case "show-mlst-related":
            panel_id = '#mlst_related_panel'
            break;
          default:
            break;
    }

    return panel_id
}
