import { GoogleLogin } from 'react-google-login';

const clientId = "GOOGLE_CLIENT_ID";

function Logout() {

    const onSuccess = () => {
        console.log("logout successful");
    }

    return (
        <div id="singOutButton">
            <GoogleLogin
            clientId={clientId}
            buttonText={"Logout"}
            onLogoutSuccess={onSuccess}
        />
     </div>
    )
}
export default Logout;