import "./main";
import $ from "jquery";

function switchTab(event) {
  event.preventDefault();

  // Handle tab validation
  let valid_tab = true;
  $(event.target)
    .closest("[role=tabpanel]")
    .find("input,textarea")
    .each(function(i, e) {
      let $e = $(e);
      let status = e.checkValidity();
      if (status === false) {
        $e.removeClass("input-filled-valid");
        $e.addClass("input-filled-invalid");
        valid_tab = false;
      }
    });

  if (valid_tab === false) {
    return;
  }

  let href = $(event.target).data("href");
  $(`.nav a[href="${href}"]`).tab("show");
}

$(() => {
  $(".tab-next").click(switchTab);
  $("input").on("keypress", function(e) {
    // Hook Enter button
    if (e.keyCode == 13) {
      e.preventDefault();
      $(e.target)
        .closest(".tab-pane")
        .find("button[data-href]")
        .click();
    }
  });

  $("#config-color-picker").on("input", function(_e) {
    $("#config-color-input").val($(this).val());
  });

  $("#config-color-reset").click(function() {
    $("#config-color-input").val("");
    $("#config-color-picker").val("");
  });

});
