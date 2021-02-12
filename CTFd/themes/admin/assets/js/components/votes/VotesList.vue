<template>
  <div>
    <div>
      <VoteCreationForm
        ref="VoteCreationForm"
        :challenge_id="challenge_id"
        @refreshVotes="refreshVotes"
      />
    </div>

    <div>
      <VoteEditForm
        ref="VoteEditForm"
        :vote_id="editing_vote_id"
        @refreshVotes="refreshVotes"
      />
    </div>

    <table class="table table-striped">
      <thead>
        <tr>
          <td class="text-center"><b>User</b></td>
          <td class="text-center"><b>Vote</b></td>
          <td class="text-center"><b>Settings</b></td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="vote in votes" :key="vote.id">
          <td class="text-center">{{ vote.user_name }}</td>
          <td class="text-center" v-if="vote.value === true">Positive</td>
          <td class="text-center" v-else>Negative</td>
          <td class="text-center">
            <i
              role="button"
              class="btn-fa fas fa-edit"
              v-if="vote.can_be_altered === true"
              @click="editVote(vote.id)"
            ></i>
            <i
              role="button"
              class="btn-fa fas fa-times"
              v-if="vote.can_be_altered === true"
              @click="deleteVote(vote.id)"
            ></i>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="col-md-12">
      <button
          class="btn btn-primary float-right"
          v-if="message === 'Add vote'"
          @click="addVote"
      >
        {{ message }}
      </button>
      <button
          class="btn btn-secondary float-right"
          disabled
          v-else-if="message !== ''"
      >
        {{ message }}
      </button>
    </div>
  </div>
</template>

<script>
import { ezQuery } from "core/ezq";
import CTFd from "core/CTFd";
import VoteCreationForm from "./VoteCreationForm.vue";
import VoteEditForm from "./VoteEditForm.vue";
export default {
  components: {
    VoteCreationForm,
    VoteEditForm
  },
  props: {
    challenge_id: Number
  },
  data: function() {
    return {
      votes: [],
      message: "",
      editing_vote_id: null
    };
  },
  methods: {
    loadVotes: function() {
      CTFd.fetch(`/api/v1/challenges/${this.$props.challenge_id}/votes`, {
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
            this.votes = response.data.votes;
            this.message = response.data.message;
          }
        });
    },
    addVote: function() {
      let modal = this.$refs.VoteCreationForm.$el;
      $(modal).modal();
    },
    editVote: function(voteId) {
      this.editing_vote_id = voteId;
      let modal = this.$refs.VoteEditForm.$el;
      $(modal).modal();
    },
    refreshVotes: function(caller) {
      this.loadVotes();
      let modal;
      switch (caller) {
        case "VoteCreationForm":
          modal = this.$refs.VoteCreationForm.$el;
          $(modal).modal("hide");
          break;
        case "VoteEditForm":
          modal = this.$refs.VoteEditForm.$el;
          $(modal).modal("hide");
          break;
        default:
          break;
      }
    },
    deleteVote: function(voteId) {
      ezQuery({
        title: "Delete Vote",
        body: "Are you sure you want to delete this vote?",
        success: () => {
          CTFd.fetch(`/api/v1/votes/${voteId}`, {
            method: "DELETE"
          })
            .then(response => {
              return response.json();
            })
            .then(data => {
              if (data.success) {
                this.loadVotes();
              }
            });
        }
      });
    }
  },
  created() {
    this.loadVotes();
  }
};
</script>

<style scoped></style>