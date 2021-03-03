import CTFd from "core/CTFd";
import nunjucks from "nunjucks";
import $ from "jquery";

window.badge = new Object();

function loadBadgeTemplate(badge) {
  console.log("data")
  $.getScript(CTFd.config.urlRoot + badge.scripts.view, function() {
    $.get(CTFd.config.urlRoot + badge.templates.create, function(
      template_data
    ) {
      const template = nunjucks.compile(template_data);
      $("#create-badge-entry-div").html(
        template.render({
          nonce: CTFd.config.csrfNonce,
          script_root: CTFd.config.urlRoot
        })
      );

      $.getScript(CTFd.config.urlRoot + badge.scripts.create, function() {
        $("#create-badge-entry-div form").submit(function(event) {
          event.preventDefault();
          const params = $("#create-badge-entry-div form").serializeJSON();
          CTFd.fetch("/api/v1/badges", {
            method: "POST",
            credentials: "same-origin",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json"
            },
            body: JSON.stringify(params)
          }).then(function(response) {
            if (response.success) {
              window.location =
                CTFd.config.urlRoot + "/admin/badges/" + response.data.id;
            }
          });
        });
      });
    });
  });
}

$.get(CTFd.config.urlRoot + "/api/v1/badges/types", function(response) {
  $("#create-badge-select").empty();
  const data = response.data;
  const badge_type_amt = Object.keys(data).length;
  if (badge_type_amt > 1) {
    const option = "<option> -- </option>";
    $("#create-badges-select").append(option);
    for (const key in data) {
      const badge = data[key];
      const option = $("<option/>");
      option.attr("value", badge.type);
      option.text(badge.name);
      option.data("meta", badge);
      $("#create-badges-select").append(option);
    }
    $("#create-badges-select-div").show();
  } else if (badge_type_amt == 1) {
    const key = Object.keys(data)[0];
    $("#create-badges-select").empty();
    loadBadgeTemplate(data[key]);
  }
});

// Adds the name, description and associated tag to the database
$("#badge-create-button").click(function() {
  // eslint-disable-nex t-line no-console
   console.log("yes");
   const params = {
        name : document.getElementsByName('badge_name'),
        description : document.getElementsByName('badge_desc'),
        type : "standard"
      };

  CTFd.api.post_award_list(params).then(response => //add an award to the database with api
  {
  if (response.success) {
    loadBadgeTemplate()
    }
  });
});


function createBadge(_event) {
  const badge = $(this)
    .find("option:selected")
    .data("meta");
  loadBadgeTemplate(badge);
}

$(() => {
  $("#create-badges-select").change(createBadge);
});
