import React, {useState} from 'react';
import Button from '@/components/Button';
export default function MyForm() {
  const [Post, setPost] = useState('');
  
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
      <label>
        Text input: <input name="myInput" value={Post} onChange={e =>setPost(e.target.value)} placeholder="Write Your Post" />
      </label>
      <Button theme="primary" label="Make Post" onPress={handleSubmit}/>
      <hr />
   </form>
  );
}

