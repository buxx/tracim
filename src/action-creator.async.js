import { FETCH_CONFIG } from './helper.js'
import {
  USER_LOGIN,
  USER_DATA,
  USER_CONNECTED,
  updateUserConnected,
  updateUserData,
  WORKSPACE,
  updateWorkspaceData,
  APP_LIST,
  setAppList
} from './action-creator.sync.js'

/*
 * fetchWrapper(obj)
 *
 * Params:
 *   An Object with the following attributes :
 *     url - string - url of the end point to call
 *     param - object - param to send with fetch call (eg. header)
 *       param.method - string - REQUIRED - method of the http call
 *     actionName - string - name of the action to dispatch with 'PENDING' and 'SUCCESS' respectively before and after the http request
 *     dispatch - func - redux dispatcher function
 *
 * Returns:
 *   An object Response generated by whatwg-fetch with a new property 'json' containing the data received or informations in case of failure
 *
 * This function create a http async request using whatwg-fetch while dispatching a PENDING and a SUCCESS redux action.
 * It also adds, to the Response of the fetch request, the json value so that the redux action have access to the status and the data
 */
const fetchWrapper = async ({url, param, actionName, dispatch, debug = false}) => {
  dispatch({type: `${param.method}/${actionName}/PENDING`})

  const fetchResult = await fetch(url, param)
  fetchResult.json = await (async () => {
    switch (fetchResult.status) {
      case 200:
      case 304:
        return fetchResult.json()
      case 204:
      case 400:
      case 404:
      case 409:
      case 500:
      case 501:
      case 502:
      case 503:
      case 504:
        return '' // @TODO : handle errors
    }
  })()
  if (debug) console.log(`fetch ${param.method}/${actionName} result: `, fetchResult)

  if ([200, 204, 304].includes(fetchResult.status)) dispatch({type: `${param.method}/${actionName}/SUCCESS`, data: fetchResult.json})
  else if ([400, 404, 500].includes(fetchResult.status)) dispatch({type: `${param.method}/${actionName}/FAILED`, data: fetchResult.json})

  return fetchResult
}

export const userLogin = (login, password, rememberMe) => async dispatch => {
  const jsonBody = JSON.stringify({
    login,
    password,
    remember_me: rememberMe
  })

  const fetchUserLogin = await fetchWrapper({
    url: 'http://localhost:3001/user/login',
    param: {
      ...FETCH_CONFIG,
      method: 'POST',
      body: jsonBody
    },
    actionName: USER_LOGIN,
    dispatch
  })
  if (fetchUserLogin.status === 200) dispatch(updateUserConnected(fetchUserLogin.json))
}

export const getIsUserConnected = () => async dispatch => {
  const fetchUserLogged = await fetchWrapper({
    url: 'http://localhost:3001/user/is_logged_in',
    param: {...FETCH_CONFIG, method: 'GET'},
    actionName: USER_CONNECTED,
    dispatch
  })
  if (fetchUserLogged.status === 200) dispatch(updateUserConnected(fetchUserLogged.json))
}

export const updateUserLang = newLang => async dispatch => {
  const fetchUpdateUserLang = await fetchWrapper({
    url: 'http://localhost:3001/user',
    param: {...FETCH_CONFIG, method: 'PATCH', body: JSON.stringify({lang: newLang})},
    actionName: USER_DATA,
    dispatch
  })
  if (fetchUpdateUserLang.status === 200) dispatch(updateUserData({lang: fetchUpdateUserLang.json.lang}))
}

// export const testResponseNoData = () => async dispatch => {
//   const fetchResponseNoData = await fetchWrapper({
//     url: 'http://localhost:3001/deletenodata',
//     param: {...FETCH_CONFIG, method: 'DELETE'},
//     actionName: 'TestNoData',
//     dispatch
//   })
//   console.log('jsonResponseNoData', fetchResponseNoData)
// }

export const getWorkspaceContent = workspaceId => async dispatch => {
  const fetchGetWorkspaceContent = await fetchWrapper({
    url: `http://localhost:3001/workspace/${workspaceId}`,
    param: {...FETCH_CONFIG, method: 'GET'},
    actionName: WORKSPACE,
    dispatch
  })
  if (fetchGetWorkspaceContent.status === 200) dispatch(updateWorkspaceData(fetchGetWorkspaceContent.json))
}

export const getAppList = () => async dispatch => {
  const fetchGetAppList = await fetchWrapper({
    url: `http://localhost:3001/app/file_content`,
    param: {...FETCH_CONFIG, method: 'GET'},
    actionName: APP_LIST,
    dispatch
  })
  if (fetchGetAppList.status === 200) dispatch(setAppList(fetchGetAppList.json))
}
