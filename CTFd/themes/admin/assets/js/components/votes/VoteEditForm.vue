<template>
  <div class="modal fade" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header text-center">
          <div class="container">
            <div class="row">
              <div class="col-md-12">
                <h3>Edit Vote</h3>
              </div>
            </div>
          </div>
          <button
            type="button"
            class="close"
            data-dismiss="modal"
            aria-label="Close"
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <form method="POST" @submit.prevent="updateVote">
          <div class="modal-body">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <div class="form-group">
                    <label class="text-muted">
                      Select your vote
                    </label>
                    <div class="form-group">
                      <select class="form-control custom-select" name="value" ref="value">
                        <option value="1" :selected="value === true">Positive</option>
                        <option value="0" :selected="value === false">Negative</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <button class="btn btn-success float-right">Submit</button>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ezAlert } from "core/ezq";
import CTFd from "core/CTFd";
export default {
  name: "VoteEditForm",
  props: {
    vote_id: Number
  },
  data: function() {
    return {
      value: null
    };
  },
  watch: {
    vote_id: {
      immediate: true,
      handler(val, oldVal) {
        if (val !== null) {
          this.loadVote();
        }
      }
    }
  },
  methods: {
    loadVote: function() {
      CTFd.fetch(`/api/v1/votes/${this.$props.vote_id}?preview=true`, {
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
            let vote = response.data;
            this.value = vote.value;
          }
        });
    },
    getValue: function() {
      return this.$refs.value.value;
    },
    updateVote: function() {
      let params = {
        challenge_id: this.$props.challenge_id,
        value: this.getValue()
      };
      CTFd.fetch(`/api/v1/votes/${this.$props.vote_id}`, {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.$emit("refreshVotes", this.$options.name);
          } else {
            ezAlert({
              title: "Error!",
              body: "You do not have the right to edit this vote",
              button: "Okay"
            });
          }
        });
    }
  },
  mounted() {
    if (this.vote_id) {
      this.loadVote();
    }
  },
  created() {
    if (this.vote_id) {
      this.loadVote();
    }
  }
};
</script>

<style scoped></style>