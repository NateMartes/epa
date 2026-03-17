import React, {useState} from 'react';
import {View, StyleSheet, TextInput} from 'react-native';
import Button from '@/components/Button';
export default function MyForm() {
  const [Uname, setUsername] = useState('');
  const [Pass, setPassword] = useState('');
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
  })
  
  function handleSubmit(e) {
  
    e.preventDefault();
    const formJson = { Username: Uname, Password: Pass };
    //fetch('/some-api', {method: form.method, body: formData });
    console.log(formJson);
    e => setPassword('');
  }

  return (
    <form method="login" onSubmit={handleSubmit}>
    	   <TextInput
	     value={Uname}
	     maxLength={100}
	     onChange={e =>setUsername(e.target.value)}
	     placeholder="Username"
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
      <View style={{alignItems: 'flex-end'}}>
      <Button theme="primary" label="Make Post" onPress={handleSubmit}/>
      </View>
      
      
   </form>
  );


}

