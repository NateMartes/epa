import {React, useState, useEffect} from 'react';
import {View, FlatList, StyleSheet, Text, StatusBar} from 'react-native';
import {SafeAreaView, SafeAreaProvider} from 'react-native-safe-area-context';
import { jwtDecode } from "jwt-decode";
import AsyncStorage from '@react-native-async-storage/async-storage';
export default function Scrollable(){
const [data, setData] = useState(null);
const [pageNo, setPageNo] = useState(0);
let loading = false;
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

const Refresh = async () => {
      }
const GetPosts = async () => {
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
const Item = ({title , content, category, created_by }) => (
  <View style={styles.item}>
    <Text style={styles.title}>{title}</Text>
    <Text style={styles.text}> {content} </Text>
    <Text style={styles.text}>  {category} {created_by} </Text>
    
  </View>
);

  const renderItem = ({ item, index }) => (
    <Item content={item.content} title={item.title} category={item.category} created_by={item.created_by}/>
  );

return(
  <SafeAreaProvider>
    <SafeAreaView style={styles.container}>
      <FlatList
        data={data}
	onMomentumScrollBegin={() => { this.onEndReachedCalledDuringMomentum = false; }}
        renderItem={renderItem}
        //keyExtractor={item => item.id}
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