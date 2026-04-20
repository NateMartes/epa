import React, {useState} from 'react';
import {View, StyleSheet, TextInput} from 'react-native';
import Button from '@/components/Button';
import { Link, useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
export default function MyForm() {

  const [Uname, setUsername] = useState('');
  const [Pass, setPassword] = useState('');
  const SubmitApi = async() => {
         const formJson = { password: Pass, email: Uname  };
         const substring = JSON.stringify(formJson);
         try {
         const response = await fetch("https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/auth/register", {
method: 'POST', body: substring, });

		if (!response.ok) {
	      	throw new Error(`HTTP error! status: ${response.status}`);
    	 }
	 const tokenData = await response.json();
	 storeData(tokenData.session_token);
         }
         catch (error){
         alert('There was an issue signing into your account, please try again');
         setPassword('');
         setUsername('');
         }
         
	 
	 }
  const storeData = async (value) => {
    try {
     await AsyncStorage.setItem('sessionID', value);
        } catch (e) {}
  };
  const router = useRouter();
  const styles = StyleSheet.create({
  input: {
    flex: 1,
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    //marginHorizontal: 200,
    borderWidth: 1,
    backgroundColor: '#fff',
    padding: 5,
    color: '#000',
    textAlignVertical: 'top',
    },
  button: {
    fontSize: 15,
    textDecorationLine: 'underLine',
    color: '#ccc',
  },
  })
  
  function handleSubmit(e) {
  
    e.preventDefault();
    SubmitApi();
    //if read data then route?
    router.navigate('/');
  }

  return (
    <form method="login" onSubmit={handleSubmit}>
    	   <TextInput
	     value={Uname}
	     maxLength={100}
	     onChange={e =>setUsername(e.target.value)}
	     placeholder="Email"
	     style={styles.input}
	   />
	   <TextInput
	     secureTextEntry
	     value={Pass}
	     maxLength={100}
	     onChange={e =>setPassword(e.target.value)}
	     placeholder="Password"
	     style={styles.input}
	   />
      <hr />
      <View style={{alignItems: 'center'}}>
      <Button label="Login" onPress={handleSubmit}/>
      <Link href="/signup" style = {styles.button}>
        Create Account
      </Link>
      </View>
      
      
   </form>
  );


}

