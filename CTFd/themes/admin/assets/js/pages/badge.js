import "./main";
import {ezQuery} from "core/ezq";
import {htmlEntities} from "core/utils";
import $ from "jquery";
import CTFd from "core/CTFd";

function addBadge() {
  let badgeName = $("#badge_name").val();
  let badgeDesc = $("#badge_desc").val();
  let badgeTag = $("#badge_tag").val();

  CTFd.api.get_tag_list().then(response => {
    let tagList = response.data;

    let matches = tagList.filter(tag => {
      return tag.id === parseInt(badgeTag);
    });
    let tagId = matches[0].id;

    const params = {
      name: badgeName,
      description: badgeDesc,
      tag_id: tagId,
    };

    CTFd.fetch("/api/v1/badges", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(params)
    }).then(response => {
      if (response.status === 200) {
        window.location = CTFd.config.urlRoot + "/admin/badges";
      }
    });
  });
}

function editBadge() {
  let badgeName = $("#badge_name").val();
  let badgeDesc = $("#badge_desc").val();
  let badgeTag = $("#badge_tag").val();

  CTFd.api.get_tag_list().then(response => {
    let tagList = response.data;

    let matches = tagList.filter(tag => {
      return tag.id === parseInt(badgeTag);
    });
    let tagId = matches[0].id;

    const params = {
      id: window.BADGE_ID,
      name: badgeName,
      description: badgeDesc,
      tag_id: tagId,
    };

    CTFd.fetch("/api/v1/badges/" + window.BADGE_ID, {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(params)
    }).then(response => {
      if (response.status === 200) {
        window.location = CTFd.config.urlRoot + "/admin/badges";
      }
    });
  });
}

$(() => {
    $("#badge-create-button").click(addBadge);

    $("#badge-edit-button").click(editBadge);

    $(".delete-badge").click(function(_event) {
    ezQuery({
      title: "Delete Badge",
      body: "Are you sure you want to delete {0}".format(
        "<strong>" + htmlEntities(window.BADGE_NAME) + "</strong>"
      ),
      success: function() {
        CTFd.fetch("/api/v1/badges/" + window.BADGE_ID, {
          method: "DELETE"
        }).then(function(response) {
          return response.json();
        }).then(function(response) {
          if (response.success) {
            window.location = CTFd.config.urlRoot + "/admin/badges";
          }
        });
      }
    });
  });
});