<template>
  <div>
    <div>
      <RessourceCreationForm
        ref="RessourceCreationForm"
        :challenge_id="challenge_id"
        @refreshRessources="refreshRessources"
      />
    </div>

    <div>
      <RessourceEditForm
        ref="RessourceEditForm"
        :ressource_id="editing_ressource_id"
        @refreshRessources="refreshRessources"
      />
    </div>

    <table class="table table-striped">
      <thead>
        <tr>
          <td class="text-center"><b>ID</b></td>
          <td class="text-center"><b>Ressource</b></td>
          <td class="text-center"><b>Settings</b></td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ressource in ressources" :key="ressource.id">
          <td class="text-center">{{ ressource.type }}</td>
          <td class="text-break">
            <pre>{{ ressource.content }}</pre>
          </td>
          <td class="text-center">
            <i
              role="button"
              class="btn-fa fas fa-edit"
              @click="editRessource(ressource.id)"
            ></i>
            <i
              role="button"
              class="btn-fa fas fa-times"
              @click="deleteRessource(ressource.id)"
            ></i>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="col-md-12">
      <button class="btn btn-success float-right" @click="addRessource">
        Create Ressource
      </button>
    </div>
  </div>
</template>

<script>
import { ezQuery } from "core/ezq";
import CTFd from "core/CTFd";
import RessourceCreationForm from "./RessourceCreationForm.vue";
import RessourceEditForm from "./RessourceEditForm.vue";
export default {
  components: {
    RessourceCreationForm,
    RessourceEditForm
  },
  props: {
    challenge_id: Number
  },
  data: function() {
    return {
      ressources: [],
      editing_ressource_id: null
    };
  },
  methods: {
    loadRessources: function() {
      CTFd.fetch(`/api/v1/challenges/${this.$props.challenge_id}/ressources`, {
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
            this.ressources = response.data;
          }
        });
    },
    addRessource: function() {
      let modal = this.$refs.RessourceCreationForm.$el;
      $(modal).modal();
    },
    editRessource: function(ressourceId) {
      this.editing_ressource_id = ressourceId;
      let modal = this.$refs.RessourceEditForm.$el;
      $(modal).modal();
    },
    refreshRessources: function(caller) {
      this.loadRessources();
      let modal;
      switch (caller) {
        case "RessourceCreationForm":
          modal = this.$refs.RessourceCreationForm.$el;
          $(modal).modal("hide");
          break;
        case "RessourceEditForm":
          modal = this.$refs.RessourceEditForm.$el;
          $(modal).modal("hide");
          break;
        default:
          break;
      }
    },
    deleteRessource: function(ressourceId) {
      ezQuery({
        title: "Delete Ressource",
        body: "Are you sure you want to delete this ressource?",
        success: () => {
          CTFd.fetch(`/api/v1/ressources/${ressourceId}`, {
            method: "DELETE"
          })
            .then(response => {
              return response.json();
            })
            .then(data => {
              if (data.success) {
                this.loadRessources();
              }
            });
        }
      });
    }
  },
  created() {
    this.loadRessources();
  }
};
</script>

<style scoped></style>