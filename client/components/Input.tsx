import React, {useState} from 'react';
import {View, StyleSheet, TextInput} from 'react-native';
import Button from '@/components/Button';
export default function MyForm() {
  const [Post, setPost] = useState('');

  const styles = StyleSheet.create({
  input: {
    flex: 1,
    height: '100%',
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
    alert(Post);
    const formJson = { PostText: Post };
    e => setPost('');
    //fetch('/some-api', {method: form.method, body: formData });
    console.log(formJson);
  }

  return (
    <form method="post" onSubmit={handleSubmit}>
    	   <TextInput
	     multiline
	     value={Post}
	     maxLength={2000}
	     onChange={e =>setPost(e.target.value)}
	     placeholder="Write Your Post"
	     style={styles.input}
	   />
      <text style={{ color:'#fff' }}>Characters Left: {Post.length}/2000</text>
      <hr />
      <View style={{alignItems: 'flex-end'}}>
      <Button theme="primary" label="Make Post" onPress={handleSubmit}/>
      </View>
      
      
   </form>
  );


}

