import { Text, View, StyleSheet } from "react-native";
import { SafeAreaView } from 'react-native-safe-area-context';
import { Link, useRouter } from 'expo-router';
import Button from '@/components/Button';
import Input from '@/components/Input';
import AsyncStorage from '@react-native-async-storage/async-storage';


export default function Index() {
  const router = useRouter();
  const storeDataAcc = async (value) => {
  try {
   await AsyncStorage.setItem('AccessID', value);
      } catch (e) {}
  };
  const removeData = async () => {
    try {
     await AsyncStorage.clear();
     router.navigate('/login');
        } catch (e) {alert('There was an issue with sign out. Please try again');}
	
  };
  return (
    <SafeAreaView style={styles.container}>
      <Button label="Sign out" onPress={removeData}/>
      <View style={styles.space}/>
      <View style={styles.link}>
      <Link href="/index" style={styles.button}>
        Create Post
      </Link>
      <Link href="/posts" style={styles.button}>
        Make Posts 
      </Link>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#00000f',
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    color: '#eee',
  },
  button: {
    fontSize: 15,
    textDecorationLine: 'underLine',
    color: '#ccc',
  },
  poster: {
    flex: 1,
    height: '100%',
    width: '100%',
    justifyContent:'center',
    alignItems: 'center',
  },
  link: {
    justifyContent: 'flex-end',
    },
  space: {
    flex: 1/3,
    },
    
});