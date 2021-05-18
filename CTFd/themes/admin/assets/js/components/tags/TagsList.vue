<template>
  <div class="col-md-12">
    <div id="results"></div>
    <div id="challenge-tags" class="my-3">
      <span
        class="badge badge-primary mx-1 challenge-tag"
        v-for="tag in tags"
        :key="tag.id"
      >
        <span>{{ tag.value }}</span>
        <a class="btn-fa delete-tag" @click="deleteTag(tag.id)"> &#215;</a>
      </span>
    </div>

    <div class="form-group">
      <label
        >Tag
        <br />
        <small class="text-muted">Type tag and press Enter</small>
      </label>
      <input
        id="tags-add-input"
        maxlength="80"
        type="text"
        class="form-control"
        v-model="tagValue"
        @keyup="setTagsList"
      />
      <div class="list-group overflow-auto" @click="addTagChallenge"></div>
    </div>
  </div>
</template>

<script>
import $ from "jquery";
import CTFd from "core/CTFd";
import { ezBadge } from "core/ezq"

export default {
  props: {
    challenge_id: Number
  },
  data: function() {
    return {
      tags: [],
      tagValue: "",
      matches: [],
      tagsList: []
    };
  },
  methods: {
    loadTags: function() {
      CTFd.fetch(`/api/v1/challenges/${this.$props.challenge_id}/tags`, {
        method: "GET",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        }
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.tags = response.data;
          }
        });
    },
    setTagsList: function(event) {
      CTFd.api.get_tag_list().then(response => {
        this.tagsList = response.data;

        this.matches = this.tagsList.filter(tag => {
          const regex = new RegExp(`^${this.tagValue}`, 'gi');
          return tag.value.match(regex) && !tag.challenges.includes(window.CHALLENGE_ID);
        });

        if (this.tagValue.length === 0) {
          this.matches = [];
          $(".list-group").html('');
        }

        this.outputHtml();

        // Check if they are new matches [WHY ?]
        let newMatches = this.tagsList.filter(tag => {
          const regex = new RegExp(`^${this.tagValue}`, 'gi');
          return tag.value.match(regex);
        });
        if (event.keyCode !== 13 || newMatches.length !== 0) {
          return;
        }

        this.addTag();
      });
    },
    addTagChallenge: function (event) {
      const params = {
        tag_id: parseInt(event.target.id),
        challenge_id: window.CHALLENGE_ID
      }
      this.matches = this.matches.filter((match) => {
        let tag = this.tagsList.filter(tag => tag.id === params.tag_id);
        return match.value !== tag[0].value;
      });

      this.outputHtml();

      CTFd.api.post_tagChallenge_list({}, params).then(res => {
        this.errorTag(res);
        CTFd.api.get_tag({ tagId: res.data.tag_id, }).then(response => {
          if (response.success) {
            this.loadTags();
          }
        });
      });
    },
    addTag: function() {
      const params = {
        value: this.tagValue,
        challenge_id: window.CHALLENGE_ID
      };
      CTFd.api.post_tag_list({}, params).then(res => {
        this.errorTag(res);
        CTFd.api.post_tagChallenge_list({}, { tag_id: res.data.id, challenge_id: window.CHALLENGE_ID }).then(response => {
          this.errorTag(response);
          if (response.success) {
            this.tagValue = "";
            this.loadTags();
          }
        });
      });
    },
    deleteTag: function(tagId) {
      CTFd.api.delete_tagChallenge({ tagId: tagId, challengeId: window.CHALLENGE_ID }).then(response => {
        if (response.success) {
          this.loadTags();
        }
      });
    },
    errorTag: function(res) {
      if (res.error === "notAllowed") {
        $("#results").append(
          ezBadge({
            type: "error",
            body: "You do not have the right to create an exercice"
          })
        );
      } else if (res.error === "alreadyAssigned") {
        $("#results").append(
          ezBadge({
            type: "error",
            body: "This task is already assigned to an exercice"
          })
        );
      }
    },
    outputHtml: function() {
      if (this.matches.length > 0) {
        const html = this.matches
            .map(
                match => `
            <a class="list-group-item list-group-item-action list-group-item-dark" id="${match.id}">${match.value}</a>
          `
            ).join('');
        $(".list-group").html(html);
      } else {
        $(".list-group").html('');
      }
    }
  },
  created() {
    this.loadTags();
  }
};
</script>

<style scoped></style>