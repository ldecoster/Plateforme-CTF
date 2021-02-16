import $ from "jquery";
import { ezToast, ezQuery } from "core/ezq";
import { htmlEntities } from "core/utils";
import CTFd from "core/CTFd";
import nunjucks from "nunjucks";

function renderSubmissionResponse(response, cb) {
  const result = response.data;

  const result_message = $("#result-message");
  const result_notification = $("#result-notification");
  const answer_input = $("#submission-input");
  result_notification.removeClass();
  result_message.text(result.message);

  if (result.status === "authentication_required") {
    window.location =
      CTFd.config.urlRoot +
      "/login?next=" +
      CTFd.config.urlRoot +
      window.location.pathname +
      window.location.hash;
    return;
  } else if (result.status === "incorrect") {
    // Incorrect key
    result_notification.addClass(
      "alert alert-danger alert-dismissable text-center"
    );
    result_notification.slideDown();

    answer_input.removeClass("correct");
    answer_input.addClass("wrong");
    setTimeout(function() {
      answer_input.removeClass("wrong");
    }, 3000);
  } else if (result.status === "correct") {
    // badge Solved
    result_notification.addClass(
      "alert alert-success alert-dismissable text-center"
    );
    result_notification.slideDown();

    $(".badge-solves").text(
      parseInt(
        $(".badge-solves")
          .text()
          .split(" ")[0]
      ) +
        1 +
        " Solves"
    );

    answer_input.val("");
    answer_input.removeClass("wrong");
    answer_input.addClass("correct");
  } else if (result.status === "already_solved") {
    // badge already solved
    result_notification.addClass(
      "alert alert-info alert-dismissable text-center"
    );
    result_notification.slideDown();

    answer_input.addClass("correct");
  } else if (result.status === "paused") {
    // CTF is paused
    result_notification.addClass(
      "alert alert-warning alert-dismissable text-center"
    );
    result_notification.slideDown();
  } else if (result.status === "ratelimited") {
    // Keys per minute too high
    result_notification.addClass(
      "alert alert-warning alert-dismissable text-center"
    );
    result_notification.slideDown();

    answer_input.addClass("too-fast");
    setTimeout(function() {
      answer_input.removeClass("too-fast");
    }, 3000);
  }
  setTimeout(function() {
    $(".alert").slideUp();
    $("#submit-key").removeClass("disabled-button");
    $("#submit-key").prop("disabled", false);
  }, 3000);

  if (cb) {
    cb(result);
  }
}

$(() => {
  $(".preview-badge").click(function(_event) {
    window.badge = {};
    $.get(
      CTFd.config.urlRoot + "/api/v1/badges/" + window.badge_ID,
      function(response) {
        const badge_data = response.data;
        badge_data["solves"] = null;

        $.getScript(
          CTFd.config.urlRoot + badge_data.type_data.scripts.view,
          function() {
            $.get(
              CTFd.config.urlRoot + badge_data.type_data.templates.view,
              function(template_data) {
                $("#badge-window").empty();
                const template = nunjucks.compile(template_data);
                window.badge.data = badge_data;
                window.badge.preRender();

                badge_data["description"] = window.badge.render(
                  badge_data["description"]
                );
                badge_data["script_root"] = CTFd.config.urlRoot;

                $("#badge-window").append(template.render(badge_data));

                $(".nav-tabs a").click(function(event) {
                  event.preventDefault();
                  $(this).tab("show");
                });

                // Handle modal toggling
                $("#badge-window").on("hide.bs.modal", function(_event) {
                  $("#submission-input").removeClass("wrong");
                  $("#submission-input").removeClass("correct");
                  $("#incorrect-key").slideUp();
                  $("#correct-key").slideUp();
                  $("#already-solved").slideUp();
                  $("#too-fast").slideUp();
                });

                $("#submit-key").click(function(event) {
                  event.preventDefault();
                  $("#submit-key").addClass("disabled-button");
                  $("#submit-key").prop("disabled", true);
                  window.badge.submit(function(data) {
                    renderSubmissionResponse(data);
                  }, true);
                  // Preview passed as true
                });

                $("#submission-input").keyup(function(event) {
                  if (event.keyCode == 13) {
                    $("#submit-key").click();
                  }
                });

                window.badge.postRender();
                window.location.replace(
                  window.location.href.split("#")[0] + "#preview"
                );

                $("#badge-window").modal();
              }
            );
          }
        );
      }
    );
  });

  $(".delete-badge").click(function(_event) {
    ezQuery({
      title: "Delete badge",
      body: "Are you sure you want to delete {0}".format(
        "<strong>" + htmlEntities(window.badge_NAME) + "</strong>"
      ),
      success: function() {
        CTFd.fetch("/api/v1/badges/" + window.badge_ID, {
          method: "DELETE"
        }).then(function(response) {
          if (response.success) {
            window.location = CTFd.config.urlRoot + "/admin/badges";
          }
        });
      }
    });
  });

  $("#badge-update-container > form").submit(function(event) {
    event.preventDefault();
    const params = $(event.target).serializeJSON(true);

    CTFd.fetch("/api/v1/badges/" + window.badge_ID, {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(params)
    }).then(function(data) {
      if (data.success) {
        ezToast({
          title: "Success",
          body: "The badge has been updated!"
        });
      }
    });
  });
});
