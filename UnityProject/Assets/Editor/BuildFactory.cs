using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEditor.Build.Reporting;
using Braemac.Factory;
public static class BuildFactory {
 [MenuItem("Braemac/Build Linux standalone")]
 public static void Build(){
  string[] args=Environment.GetCommandLineArgs();string output="../builds/linux/FactoryGalaxy.x86_64";
  for(int i=0;i<args.Length-1;i++)if(args[i]=="--build-output")output=args[i+1];
  var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
  new GameObject("Factory application").AddComponent<FactoryApp>();
  Directory.CreateDirectory("Assets/Scenes");Directory.CreateDirectory("Assets/Resources");
  if(!File.Exists("Assets/Resources/FactoryStandard.mat"))AssetDatabase.CreateAsset(new Material(Shader.Find("Standard")),"Assets/Resources/FactoryStandard.mat");
  EditorSceneManager.SaveScene(scene,"Assets/Scenes/Factory.unity");AssetDatabase.SaveAssets();
  PlayerSettings.companyName="Braemac";PlayerSettings.productName="GTS Factory Galaxy";
  PlayerSettings.defaultScreenWidth=1600;PlayerSettings.defaultScreenHeight=900;PlayerSettings.fullScreenMode=FullScreenMode.Windowed;
  PlayerSettings.runInBackground=true;PlayerSettings.SetScriptingBackend(UnityEditor.Build.NamedBuildTarget.Standalone,ScriptingImplementation.Mono2x);
  Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output)));
  bool previousResize=PlayerSettings.resizableWindow;
  try {
  for(int i=0;i<args.Length-1;i++)if(args[i]=="--resizable-window")PlayerSettings.resizableWindow=args[i+1]=="true";
  var result=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{"Assets/Scenes/Factory.unity"},locationPathName=output,target=BuildTarget.StandaloneLinux64,options=BuildOptions.None});
  Debug.Log("FACTORY_BUILD "+result.summary.result+" bytes "+result.summary.totalSize);
  if(result.summary.result!=BuildResult.Succeeded)throw new Exception("Linux standalone build failed");
  } finally {PlayerSettings.resizableWindow=previousResize;AssetDatabase.SaveAssets();}
 }
}
