// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.5.0/firebase-app.js";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyAc_veZWFlMCqBp988qL2Qn87oFudB9ylk",
    authDomain: "virtual-pet-calendar.firebaseapp.com",
    projectId: "virtual-pet-calendar",
    storageBucket: "virtual-pet-calendar.appspot.com",
    messagingSenderId: "304356571830",
    appId: "1:304356571830:web:fb97be2ab5f328719bc417",
    measurementId: "G-1MERZLVR8Z"
};

const app = initializeApp(firebaseConfig);

export default app;