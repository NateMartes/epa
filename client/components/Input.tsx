import React, {useState} from 'react';
import {View, StyleSheet, TextInput} from 'react-native';
import Button from '@/components/Button';
import { Dropdown } from 'react-native-paper-dropdown';
import { Provider as PaperProvider } from 'react-native-paper';
export default function MyForm() {
  const [Post, setPost] = useState('');
  const [Slug, setSlug] = useState('');
  const [Title, setTitle] = useState('');
  const OPTIONS = [
  { label: 'electrical hazard', value: 'electrical hazard' },
  { label: 'Female', value: 'female' },
  { label: 'Other', value: 'other' },
  ];
  const SubmitApi = async() => {
         const formJson = { title: Title, email: Uname  };
         const substring = JSON.stringify(formJson);

         const response = await fetch("https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/auth/login", {
method: 'POST',headers: { 'Content-Type': 'application/json'}, body: substring, });
         const responseJson = await response.json();

         if (!response.ok) {
            alert(`Error: ${responseJson.detail}`);
            console.log(`HTTP error, status: ${response.status}`);
            setPassword('');
            setUsername('');
         }
         else{
            storeData(responseJson.session_token);
            router.navigate('/');
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
      <View style={{alignItems: 'flex-end'}}>
       	   <TextInput
	     multiline
	     value={Title}
	     maxLength={50}
	     onChange={e =>setTitle(e.target.value)}
	     placeholder="PostTitle"
	     style={styles.input}
	   />
	   <PaperProvider>
      <View style={{ margin: 16 }}>
        <Dropdown
          label="Category"
          placeholder="Select Category"
          options={OPTIONS}
          value={Slug}
          onSelect={setSlug}
        />
      </View>
    </PaperProvider>
      </View>
      <View style={{alignItems: 'flex-end'}}>
      <Button theme="primary" label="Make Post" onPress={handleSubmit}/>
      </View>
      
      
   </form>
  );


}

