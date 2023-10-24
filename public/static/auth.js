import { GoogleAuthProvider, getAuth, signInWithPopup, signOut } from "https://www.gstatic.com/firebasejs/10.5.0/firebase-auth.js";

function signIn() {
    const provider = new GoogleAuthProvider();
    const auth = getAuth()

    // request access to google calendar
    provider.addScope('https://www.googleapis.com/auth/calendar');

    //  applies default browser preference language
    auth.useDeviceLanguage();

    signInWithPopup(auth, provider).then((result) => {
        // gives google access token to access google api
        const credential = GoogleAuthProvider.credentialFromResult(result);
        const token = credential.accessToken;

        // signed-in user info
        const user = result.user;
    }).catch((error) => {
        // handle errors here
        const errorCode = error.code;
        const errorMessage = error.message;

        // email of the user's account used.
        const email = error.customData.email;

        // authcredential type that was used
        const credential = GoogleAuthProvider.credentialFromError(error);
    });
};

function logout() {
    signOut(auth).then(() => {
        // success in sign-out
    }).catch((error) => {
        // error occured
    });
};

$("#login-btn").click(signIn)
