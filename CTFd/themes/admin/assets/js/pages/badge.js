import "./main";
import "core/utils";
import $ from "jquery";
import "bootstrap/js/dist/tab";
import CTFd from "core/CTFd";
import { htmlEntities } from "core/utils";
import { ezQuery, ezAlert, ezToast } from "core/ezq";
import { default as helpers } from "core/helpers";
import { bindMarkdownEditors } from "../styles";
import Vue from "vue/dist/vue.esm.browser";
import CommentBox from "../components/comments/CommentBox.vue";


const displayHint = data => {
  ezAlert({
    title: "Hint",
    body: data.html,
    button: "Got it!"
  });
};

const loadHint = id => {
  CTFd.api.get_hint({ hintId: id, preview: true }).then(response => {
    if (response.data.content) {
      displayHint(response.data);
      return;
    }
    // displayUnlock(id);
  });
};

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
    setTimeout(function () {
      answer_input.removeClass("wrong");
    }, 3000);
  } else if (result.status === "correct") {
    // Challenge Solved
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
    // Challenge already solved
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
    setTimeout(function () {
      answer_input.removeClass("too-fast");
    }, 3000);
  }
  setTimeout(function () {
    $(".alert").slideUp();
    $("#badge-submit").removeClass("disabled-button");
    $("#badge-submit").prop("disabled", false);
  }, 3000);

  if (cb) {
    cb(result);
  }
}

function loadBadgeTemplate(badge) {
  CTFd._internal.badge = {};
  $.getScript(CTFd.config.urlRoot + badge.scripts.view, function () {
    let template_data = badge.create;
    $("#create-badge-entry-div").html(template_data);
    bindMarkdownEditors();

    $.getScript(CTFd.config.urlRoot + badge.scripts.create, function () {
      $("#create-badge-entry-div form").submit(function (event) {
        console.log("create detecté");
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
        })
          .then(function (response) {
            return response.json();
          })
          .then(function (response) {
            if (response.success) {
              $("#badge-create-options #badge_id").val(
                response.data.id
              );
              $("#badge-create-options").modal();
            }
          });
      });
    });
  });
}

function addBadge(event) {
  console.log("create detecté");
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
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (response) {
      if (response.success) {
        $("#badge-create-options #badge_id").val(
          response.data.id
        );
        $("#badge-create-options").modal();
      }
    });
}

function handleBadgeOptions(event) {
  event.preventDefault();
  var params = $(event.target).serializeJSON(true);
  let flag_params = {
    badge_id: params.badge_id,
    content: params.flag || "",
    type: params.flag_type,
    data: params.flag_data ? params.flag_data : ""
  };
  // Define a save_challenge function
  let save_badge = function () {
    CTFd.fetch("/api/v1/badges/" + params.badge_id, {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        state: params.state
      })
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        if (data.success) {
          setTimeout(function () {
            window.location =
              CTFd.config.urlRoot + "/admin/badges/" + params.badge_id;
          }, 700);
        }
      });
  };

  Promise.all([
    // Save flag
    new Promise(function (resolve, _reject) {
      if (flag_params.content.length == 0) {
        resolve();
        return;
      }
      CTFd.fetch("/api/v1/flags", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(flag_params)
      }).then(function (response) {
        resolve(response.json());
      });
    }),
    // Upload files
    new Promise(function (resolve, _reject) {
      let form = event.target;
      let data = {
        badge: params.badge_id,
        type: "badge"
      };
      let filepath = $(form.elements["file"]).val();
      if (filepath) {
        helpers.files.upload(form, data);
      }
      resolve();
    })
  ]).then(_responses => {
    save_badge();
  });
}

$(() => {
  $(".preview-badge").click(function (_e) {
    CTFd._internal.badge = {};
    $.get(
      CTFd.config.urlRoot + "/api/v1/badges/" + window.BADGE_ID,
      function (response) {
        // Preview should not show any solves
        const badge_data = response.data;
        badge_data["solves"] = null;

        $.getScript(
          CTFd.config.urlRoot + badge_data.type_data.scripts.view,
          function () {
            const badge = CTFd._internal.badge;

            // Inject challenge data into the plugin
            badge.data = response.data;

            $("#badge-window").empty();

            // Call preRender function in plugin
            badge.preRender();

            $("#badge-window").append(badge_data.view);

            $("#badge-window #badge-input").addClass("form-control");
            $("#badge-window #badge-submit").addClass(
              "btn btn-md btn-outline-secondary float-right"
            );

            $(".badge-solves").hide();
            $(".nav-tabs a").click(function (e) {
              e.preventDefault();
              $(this).tab("show");
            });

            // Handle modal toggling
            $("#badge-window").on("hide.bs.modal", function (_event) {
              $("#badge-input").removeClass("wrong");
              $("#badge-input").removeClass("correct");
              $("#incorrect-key").slideUp();
              $("#correct-key").slideUp();
              $("#already-solved").slideUp();
              $("#too-fast").slideUp();
            });

            $(".load-hint").on("click", function (_event) {
              loadHint($(this).data("hint-id"));
            });

            $("#badge-submit").click(function (e) {
              e.preventDefault();
              $("#badge-submit").addClass("disabled-button");
              $("#badge-submit").prop("disabled", true);
              CTFd._internal.badge
                .submit(true)
                .then(renderSubmissionResponse);
              // Preview passed as true
            });

            $("#badge-input").keyup(function (event) {
              if (event.keyCode == 13) {
                $("#badge-submit").click();
              }
            });

            badge.postRender();
            window.location.replace(
              window.location.href.split("#")[0] + "#preview"
            );

            $("#badge-window").modal();
          }
        );
      }
    );
  });

  $(".delete-badge").click(function (_e) {
    ezQuery({
      title: "Delete Badge",
      body: "Are you sure you want to delete {0}".format(
        "<strong>" + htmlEntities(window.BADGE_NAME) + "</strong>"
      ),
      success: function () {
        CTFd.fetch("/api/v1/badges/" + window.BADGE_ID, {
          method: "DELETE"
        })
          .then(function (response) {
            return response.json();
          })
          .then(function (response) {
            if (response.success) {
              window.location = CTFd.config.urlRoot + "/admin/badges";
            }
          });
      }
    });
  });

  $("#badge-update-container > form").submit(function (e) {
    e.preventDefault();
    const params = $(e.target).serializeJSON(true);

    CTFd.fetch("/api/v1/badges/" + window.BADGE_ID + "/flags", {
      method: "GET",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      }
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (response) {
        let update_badge = function () {
          CTFd.fetch("/api/v1/badges/" + window.BADGE_ID, {
            method: "PATCH",
            credentials: "same-origin",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json"
            },
            body: JSON.stringify(params)
          })
            .then(function (response) {
              return response.json();
            })
            .then(function (response) {
              if (response.success) {
                $(".badge-state").text(response.data.state);
                switch (response.data.state) {
                  case "visible":
                    $(".badge-state")
                      .removeClass("badge-danger")
                      .removeClass("badge-warning")
                      .addClass("badge-success");
                    break;
                  case "voting":
                    $(".badge-state")
                      .removeClass("badge-success")
                      .removeClass("badge-danger")
                      .addClass("badge-warning");
                    break;
                  case "hidden":
                    $(".badge-state")
                      .removeClass("badge-success")
                      .removeClass("badge-warning")
                      .addClass("badge-danger");
                    break;
                  default:
                    break;
                }
                ezToast({
                  title: "Success",
                  body: "The Badge has been updated!"
                });
              } else {
                let body_message = "";
                if (response.errors === "votes") {
                  body_message = "Not enough positive votes for this challenge!";
                } else {
                  body_message = "The challenge can't be updated!";
                }
                ezToast({
                  title: "Error",
                  body: body_message
                });
              }
            });
        };
        // Check if the challenge doesn't have any flags before marking visible
        if (response.data.length === 0 && params.state === "visible") {
          ezQuery({
            title: "Missing Flags",
            body:
              "This challenge does not have any flags meaning it may be unsolveable. Are you sure you'd like to update this challenge?",
            success: update_badge
          });
        } else {
          update_badge();
        }
      });
  });

  $("#create-badge").submit(addBadge);

  $("#prerequisite-add-form").submit(addRequirement);
  $(".delete-requirement").click(deleteRequirement);

  $("#hint-add-button").click(showHintModal);
  $(".delete-hint").click(deleteHint);
  $(".edit-hint").click(showEditHintModal);
  $("#hint-edit-form").submit(editHint);

  $("#flag-add-button").click(addFlagModal);
  $("#flags-create-select").change(flagTypeSelect);
  $(".edit-flag").click(editFlagModal);

  $("#vote-add-button").click(addVoteModal);
  $(".delete-vote").click(deleteVote);
  $(".edit-vote").click(editVoteModal);

  // Because this JS is shared by a few pages,
  // we should only insert the CommentBox if it's actually in use
  if (document.querySelector("#comment-box")) {
    // Insert CommentBox element
    const commentBox = Vue.extend(CommentBox);
    let vueContainer = document.createElement("div");
    document.querySelector("#comment-box").appendChild(vueContainer);
    new commentBox({
      propsData: { type: "badge", id: window.BADGE_ID }
    }).$mount(vueContainer);
  }

  $.get(CTFd.config.urlRoot + "/api/v1/badges/types", function (response) {
    const data = response.data;
    loadBadgeTemplate(data["standard"]);

    $("#create-badges-select input[name=type]").change(function () {
      let badge = data[this.value];
      loadBadgeTemplate(badge);
    });
  });
});
