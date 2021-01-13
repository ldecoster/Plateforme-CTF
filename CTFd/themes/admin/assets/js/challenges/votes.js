import $ from "jquery";
import CTFd from "core/CTFd";
import nunjucks from "nunjucks";
import { ezQuery } from "core/ezq";

export function deleteVote(event) {
  event.preventDefault();
  const vote_id = $(this).attr("vote-id");
  const row = $(this)
    .parent()
    .parent();

  ezQuery({
    title: "Remove Vote",
    body: "Are you sure you want to remove your vote?",
    success: function() {
      CTFd.fetch("/api/v1/votes/" + vote_id, {
        method: "DELETE"
      })
        .then(function(response) {
          return response.json();
        })
        .then(function(response) {
          if (response.success) {
            row.remove();
          }
        });
    }
  });
}

export function addVoteModal(event) {
  event.preventDefault();
  $.get(CTFd.config.urlRoot + "/api/v1/votes/types", function(
    response
  ) {
    const data = response.data;
    $.get(CTFd.config.urlRoot + data.templates.create, function(template_data) {
      $("#create-votes form").empty();
      $("#create-votes form").off();

      const template = nunjucks.compile(template_data);
      $("#create-votes form").append(template.render(data));

      $("#create-votes form").submit(function(event) {
        event.preventDefault();
        const params = $("#create-votes form").serializeJSON(true);
        params["challenge_id"] = window.CHALLENGE_ID;
        CTFd.fetch("/api/v1/votes", {
          method: "POST",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify(params)
        })
        .then(function(response) {
          return response.json();
        })
        .then(function(_response) {
          window.location.reload();
        });
      });
      $("#create-votes").modal();
    });
  });
}

export function editVoteModal(event) {
  event.preventDefault();
  const vote_id = $(this).attr("vote-id");
  const row = $(this)
    .parent()
    .parent();

  $.get(CTFd.config.urlRoot + "/api/v1/votes/" + vote_id, function(response) {
    const data = response.data;
    $.get(CTFd.config.urlRoot + data.templates.update, function(template_data) {
      $("#edit-votes form").empty();
      $("#edit-votes form").off();

      const template = nunjucks.compile(template_data);
      $("#edit-votes form").append(template.render(data));

      $("#edit-votes form").submit(function(event) {
        event.preventDefault();
        const params = $("#edit-votes form").serializeJSON();

        CTFd.fetch("/api/v1/votes/" + vote_id, {
          method: "PATCH",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify(params)
        })
          .then(function(response) {
            return response.json();
          })
          .then(function(response) {
            if (response.success) {
              $(row)
                .find(".vote-value")
                .text(response.data.value === true ? "Positive" : "Negative");
              $("#edit-votes").modal("toggle");
            }
          });
      });
      $("#edit-votes").modal();
    });
  });
}