/*
    results.html
*/
function show_panel(navbar_id) {
    panel_id = get_panel_id(navbar_id);
    $(panel_id).removeClass('hide')
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
          default:
            break;
    }

    return panel_id
}
