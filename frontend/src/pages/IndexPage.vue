<template>
  <div class="background">
    <div>
      <q-input
        outlined
        v-model="searchText"
        label="Search"
        debounce="500"
        class="text-body1 text-weight-bolder"
        @update:model-value="retrieveAllPhotos()"
      >
        <template v-slot:prepend>
          <q-icon name="search" />
        </template>
      </q-input>
    </div>
    <div class="library-content">
      <div v-for="idx in libraryPhotoURLs.length" :key="idx" :class="getSize()">
        <!-- q-btn icon="close" stack glossy color="red" @click="deletePhoto(libraryPhotoIds[idx-1])" /-->
        <div class="pin-modal">
          <div class="modal-head">
            <div class="save-card">Save</div>
          </div>
        </div>
        <div class="pin-photo">
          <img :src="libraryPhotoURLs[idx-1]" style="opacity: 1; max-width: 100%;" />
        </div>
      </div>
    </div>
    <div class="upload-content">
      <div class="row">
        <div class="col-6" align="end">
          <q-avatar v-if="selectedPhotoURL==''" size="80px" font-size="80px" color="red" text-color="white" icon="image" class="image-icon" />
          <q-img
            v-if="selectedPhotoURL"
            :src="selectedPhotoURL"
            class="photo-preview"
          >
          </q-img>
        </div>
        <input 
          style="display: none" 
          type="file" 
          @change="onFileSelected"
          ref="photoInput">
        <q-btn
          label="Pick Photo"
          outline
          type="submit"
          class="outlined-button pick-button text-body1 text-weight-bolder"
          @keydown.enter.prevent
          @click="($refs.photoInput as any).click()"
        ></q-btn>
      </div>
      <div v-if="message" class="alert" role="alert">
        {{ message }}
      </div>
      <div class="upload-btn-position">
        <q-btn
          label="upload"
          type="submit"
          icon-right="chevron_right"
          outline
          class="outlined-button text-body1 text-weight-bolder"
          @click="savePhoto"
        ></q-btn>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';
import { Buffer } from 'buffer';

export default defineComponent({
  name: 'IndexPage',
  components: {},
  data() {
    return {
      selectedPhoto: null as File | null,
      selectedPhotoURL: '',
      message: '',
      searchText: '',
      libraryPhotoURLs: [] as string[],
    }
  },
  mounted(){
    this.retrieveAllPhotos();
  },
  methods: {
    getSize(){
      const size = Math.random();
      var class_name = '';
      if(size < 0.33) class_name = 'card-small';
      else if(size < 0.66) class_name = 'card-medium';
      else class_name = 'card-large';
      return 'photo-card ' + class_name;
    },
    onFileSelected(event: Event){
      const target = event.target as HTMLInputElement;
      if(target.files != null && target.files.length >= 1) {
        this.selectedPhoto = target.files[0];
        if(this.selectedPhoto == null)
          return;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.selectedPhotoURL = e.target?.result as string;
        };
        reader.readAsDataURL(this.selectedPhoto);
      }
    },
    savePhoto(){
      if(this.selectedPhoto == null) {
        this.message = 'Please choose a file first';
        return;
      }
      if(this.selectedPhoto.size > 3*1024*1024) {
        this.message = 'File too large. Max size 3 Mb';
        return;
      }
      this.uploadPhoto(this.selectedPhoto);
    },
    uploadPhoto(photo:File){
      const api = axios.create({ baseURL: 'http://localhost:8000' });
      const formData = new FormData();
      formData.append('file', photo, photo.name);
      api.post('/uploadPhoto/', formData, { headers: {
        'Content-Type': 'multipart/form-data'
      }});
    },
    // retrieve Photo by id and store its URL in libraryPhotoURLs[idx]
    retrievePhoto(id:string, idx:number){
      const api = axios.create({ baseURL: 'http://localhost:8000' });
      api.put(`/retrievePhoto/${id}`, {})
      .then((resp)=>{
        const buff = Buffer.from(resp.data, 'base64');
        const blob = new Blob([buff], { type: 'image/png' });
        const photo = new File([blob], 'test', { type: 'image/png' });
        const reader = new FileReader();
        reader.onload = (e) => {
          this.libraryPhotoURLs[idx] = e.target?.result as string;
        };
        reader.readAsDataURL(photo as File);
      })
      .catch((err)=>{
        console.log(err)
      });
    },
    retrieveAllPhotos(){
      const api = axios.create({ baseURL: 'http://localhost:8000' });
      api.put(`/retrieveAllPhotoInfo?text=${this.searchText}`, {})
      .then((resp)=>{
        // an array of object IDs
        const all_photo_info = resp.data.data; 
        this.libraryPhotoURLs = (new Array(all_photo_info.length)).fill('');
        for(let i=0;i<all_photo_info.length;i++) {
          this.retrievePhoto(all_photo_info[i], i);
        }
      })
      .catch((err)=>{
        console.log(err);
      });
    },
  },
});
</script>
<style lang="scss" scoped>
.background {
  padding: 10%;
  height: 100%;
}
.library-content {
  padding: 0;
  margin: 0;
  width: 80vw;
  display: grid;
  grid-template-columns: repeat(auto-fill, 250px);
  grid-auto-rows: 10px;
  justify-content: center;
}
.photo-card {
  grid-row-end: span 28;
  margin: 15px 10px;
  padding: 0;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}
.pin-modal {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  background-color: rgba(0, 0, 0, 0.1);
  transition-duration: 0.3s;
}
.pin-modal:hover {
  opacity: 1;
}
.pin-modal .modal-head {
  width: 100%;
  height: 20%;
  position: fixed;
  top: 0;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
.pin-modal .modal-head .save-card {
  margin-right: 20px;
  width: 60px;
  height: 40px;
  border-radius: 22px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  font-weight: 700;
  color: white;
  background-color: rgba(188,38,26);
  cursor: pointer;
}
.pin-modal .modal-head .save-card:hover {
  background-color: rgb(138, 26, 18);
}
.pin-photo {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #eeeeee;
}
.card-small {
  grid-row-end: span 26;
}

.card-medium {
  grid-row-end: span 33;
}

.card-large {
  grid-row-end: span 45;
}
.upload-content {
  align-items: center;
  justify-content: center;
  padding: 5%;
}
.image-icon{
  margin-right: 10%;
  margin-left: 10%;
}
.pick-button{
  height: 40px;
  margin-top: 15px;
  margin-bottom: 10px;
}
.alert {
  color: red;
  text-align: center;
  margin-top: 5%;
}
.upload-btn-position {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  margin-top: 5%;
}
.photo-preview {
  width: 80px;
  max-width: 100%;
  height: 80px;
  max-height: 100%;
  border-radius: 50%;
  margin-right: 10%;
  margin-left: 20%;
  border-radius: 16px;
  background: grey;
}
</style>