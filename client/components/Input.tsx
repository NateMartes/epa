import React, {useState} from 'react';
import {View, StyleSheet, TextInput} from 'react-native';
import Button from '@/components/Button';
import { Dropdown } from 'react-native-paper-dropdown';
import { Provider as PaperProvider } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
export default function MyForm() {
  const [Post, setPost] = useState('');
  const [Slug, setSlug] = useState('');
  const [Title, setTitle] = useState('');
  const OPTIONS = [
  { label: 'Test-1', value: 'test-1' },
  { label: 'Test-2', value: 'test-2' },
  { label: 'Test-3', value: 'test-3' },
  ];  
  const PostApi = async() => {
         const formJson = { title: Title, content: Post, category_slug: Slug  };
         const substring = JSON.stringify(formJson);
	 const token = await AsyncStorage.getItem('AccessID');
         const response = await fetch("https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/post", {
method: 'POST',headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: substring, });
         const responseJson = await response.json();
	 
         if (!response.ok) {
            alert(`Error: ${responseJson.detail}`);
            console.log(`HTTP error, status: ${response.status}`);
         }
         else{
            alert('Post Submitted!');
            setPost('');
	    setTitle('');
	    setSlug('');
         }
}
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
  smallInput: {
    flex: 1,
    height: '50%',
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    //marginHorizontal: 200,
    borderWidth: 1,
    backgroundColor: '#fff',
    paddingVertical: 0,
    color: '#000',
    textAlignVertical: 'top',
    },
  })
  
  function handleSubmit(e) {
  
    const formJson = { PostText: Post };
    PostApi(Post);
    e => setPost('');
    
    
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
      <View style={{paddingVertical: 0, alignItems: 'flex-end'}}>
       	   <TextInput
	     multiline
	     value={Title}
	     maxLength={50}
	     onChange={e =>setTitle(e.target.value)}
	     placeholder="Post Title"
	     style={styles.smallInput}
	   />
      </View>
      <View style={{paddingVertical: 0, alignItems: 'flex-end'}}>
       	   <TextInput
	     multiline
	     value={Slug}
	     maxLength={50}
	     onChange={e =>setSlug(e.target.value)}
	     placeholder="Post Tag"
	     style={styles.smallInput}
	   />
	 
      </View>
     
      <hr />
      <View style={{alignItems: 'flex-end'}}>
      <Button type="submit" theme="primary" label="Make Post" onPress={handleSubmit}/>
      </View>
      
      
   </form>
  );


}

