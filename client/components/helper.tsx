import AsyncStorage from '@react-native-async-storage/async-storage';
import { Link, useRouter } from 'expo-router';
router = useRouter();
export const reauth = async () => {
        const token = AsyncStorage.getItem('sessionID');
        const response = await fetch("https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/auth/session", {
method: 'POST',headers: { 'Content-Type': 'application/json' , 'Authorization': `Bearer ${token}`}, });

        if(!response.ok){
                removeData();
                console.log(`HTTP error, status: ${response.status}`);
        }
        else{
        responseJson = await response.json();
        storeDataAcc(responseJson.access_token);
                }
                }
 export const removeData = async () => {
    //try {

     await AsyncStorage.clear();
     router.navigate('/login');
        //} catch (e) {
	//alert('There was an issue with sign out. Please try again');}
	//alert(`${e}`);
	

  };