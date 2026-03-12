import React, {useState} from 'react';
import {View, StyleSheet, TextInput} from 'react-native';
import Button from '@/components/Button';
import { Link } from 'expo-router';
export default function MyForm() {
  const [Uname, setUsername] = useState('');
  const [Pass, setPassword] = useState('');
  const [Emails, setEmail] = useState('');
  const [PassTwo, setPasswordTwo] = useState('');
 
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
    if (Pass != PassTwo){
       alert('Passwords must match.');
       setPassword('');
       setPasswordTwo('');
       }
    else {
    	 
    	 const formJson = { Username: Uname, Password: Pass, Email: Emails  };
    	 //fetch('/some-api', {method: form.method, body: formData });
    	 console.log(formJson);
    	 e => setPassword('');
  	 }
}

  return (
    <form method="signup" onSubmit={handleSubmit}>
           <TextInput
	     value={Emails}
	     maxLength={100}
	     onChange={e =>setEmail(e.target.value)}
	     placeholder="Enter Email"
	     style={styles.input}
	   />
    	   <TextInput
	     value={Uname}
	     maxLength={100}
	     onChange={e =>setUsername(e.target.value)}
	     placeholder="Create Username"
	     style={styles.input}
	     />
	 <View style={{flexDirection: "row"}}>
	   <TextInput
	     secureTextEntry
	     value={Pass}
	     maxLength={100}
	     onChange={e =>setPassword(e.target.value)}
	     placeholder="Set Password"
	     style={styles.input}
	   />
	   <TextInput
	     secureTextEntry
	     value={PassTwo}
	     maxLength={100}
	     onChange={e =>setPasswordTwo(e.target.value)}
	     placeholder="Repeat Password"
	     style={styles.input}
	   />
	 </View>
      <hr />
      <View style={{alignItems: 'center'}}>
      <Button label="Sign Up" onPress={handleSubmit}/>
      <Link href="/login" style = {styles.button}>
        Return to Sign In
      </Link>
      </View>
      
      
   </form>
  );


}

