import {React, useState, useEffect} from 'react';
import {View, FlatList, StyleSheet, Text, StatusBar} from 'react-native';
import {SafeAreaView, SafeAreaProvider} from 'react-native-safe-area-context';
import { Link, useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
export default function Scrollable(){
const [data, setData] = useState(null);
const [pageNo, setPageNo] = useState(0);
let loading = false;
const router = useRouter();
const baseUrl = "https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/post" 
const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginTop: StatusBar.currentHeight || 0,
  },
  item: {
    backgroundColor: '#f0f0f0',
    padding: 20,
    marginVertical: 8,
    marginHorizontal: 16,
  },
  title: {
    fontSize: 32,
  },
  text: {
    fontSize: 16
  }
});
const reauth = async () => {
        const token = AsyncStorage.getItem('sessionID');
        const response = await fetch("https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/auth/session", {
method: 'POST',headers: { 'Content-Type': 'application/json' , 'Authorization': `Bearer ${token}`}, });

        if(!response.ok){
                //removeData();
                console.log(`HTTP error, status: ${response.status}`);
        }
        else{
        responseJson = await response.json();
        storeDataAcc(responseJson.access_token);
                }
                }
const removeData = async () => {
    try {

     await AsyncStorage.clear();
     router.navigate('/login');
        } catch (e) {
        alert('There was an issue with sign out. Please try again');}


  };
const Refresh = async () => {
      }
const GetPosts = async () => {
      //reauth();
      const token = await AsyncStorage.getItem('AccessID');
   const response = await fetch('https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/post?' + new URLSearchParams({page_num: pageNo}).toString(), {
   	 method: 'GET',headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` } });
	   const responseJson = await response.json();
	 if (!response.ok){
	 alert(`Error: ${responseJson.detail}`);
	 console.log(`HTTP error, status: ${response.status}`);
	 }
	 else{
  setPageNo(pageNo +1)
  const data = responseJson.posts;
  console.log(data);
  setData(data);
  }
};


useEffect(() => {
    setPageNo(0);
    GetPosts();
  }, []);
//type ItemProps = {title: string, content: string, created_by: string, category: string };

const getMorePosts = async () => {
      //reauth();
      const token = await AsyncStorage.getItem('AccessID');
const response = await fetch('https://01xioere1a.execute-api.us-west-2.amazonaws.com/Prod/v1/post?' + new URLSearchParams({page_num: pageNo}).toString(), {
   	 method: 'GET',headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` } });	 if (!response.ok)
	 {
	 alert(`Error: ${responseJson.detail}`);
	 console.log(`HTTP error, status: ${response.status}`);
	 }
	 else{
	 setPageNo(pageNo + 1);
	 const responseJson = await response.json();
  	 const newData = responseJson.posts;
	 loading = false;
     	 setData((data) => [...data, ...newData]);
	 }
};
const Item = ({title , content, category, username }) => (
  <View style={styles.item}>
    <Text style={styles.title}>{title}</Text>
    <Text style={styles.text}> {content} </Text>
    <Text style={styles.text}>  {username} {category}</Text>
    
  </View>
);

  const renderItem = ({ item, index }) => (
    <Item content={item.content} title={item.title} category={item.category} username={item.username}/>
  );

return(
  <SafeAreaProvider>
    <SafeAreaView style={styles.container}>
      <FlatList
        data={data}
	onMomentumScrollBegin={() => { this.onEndReachedCalledDuringMomentum = false; }}
        renderItem={renderItem}
	onEndReachedThreshold={0.2} 
  	onEndReached={({ distanceFromEnd }) => {
  		if (distanceFromEnd < 0) return;
  		if (loading) return;
		loading = true;
  		getMorePosts();
  	}	}
      />
    </SafeAreaView>
  </SafeAreaProvider>
);


}